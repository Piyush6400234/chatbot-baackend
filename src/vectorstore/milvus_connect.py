from langchain_community.vectorstores.milvus import Milvus
from src.app.config import setting
from langchain.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from docx import Document as Documentx
from langchain_community.embeddings import AzureOpenAIEmbeddings
from io import BytesIO
import tempfile
from pymilvus import connections, Collection
import os
from docx.table import Table
from docx.text.paragraph import Paragraph



embeddings = AzureOpenAIEmbeddings(
    azure_deployment=setting.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    openai_api_key=setting.AZURE_OPENAI_API_KEY,
    openai_api_version=setting.AZURE_OPENAI_API_VERSION,
    openai_api_type="azure",
    chunk_size=1000,
    validate_base_url=False

)

connections.connect(
    alias="default",
    uri=setting.ZILLIS_ENDPOINT,
    token=setting.ZILLIS_TOKEN,
)

class MilvusStore:
    def __init__(self):
        self.mulvus_url = setting.ZILLIS_ENDPOINT
        self.milvus_token = setting.ZILLIS_TOKEN
        
        
    async def get_vectorstore(self, collection_name: str):
        vector_store = Milvus(
            embeddings,
            collection_name=collection_name,
            connection_args = {"uri": self.mulvus_url, "token": self.milvus_token}
        )
        return vector_store


    async def search_vectorStore(self, query, vector_store):
        return await vector_store.asimilarity_search_with_score(query)



    async def load_doc_to_milvus(self, docs):
        vectorstore = await self.get_vectorstore(setting.ZILLIS_COLLECTION_NAME)
        await vectorstore.add_texts(docs)

        
    def load_document_from_bytes(self, file_bytes, suffix):
        text_splitter_docx = RecursiveCharacterTextSplitter(
                chunk_size=5000,  # Very large, because we don't want splits inside paragraphs
                chunk_overlap=0
            )
    
    # For PDFs we still want normal chunking
        text_splitter_pdf = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(file_bytes)

            tmp_file.flush()
            
            docs = []
            # Use the path of the temporary file for PyPDFLoader
            if suffix == ".docx":
                doc = Documentx(BytesIO(file_bytes))
                for block in self.iter_block_items(doc):
                    if isinstance(block, Paragraph):
                        text = block.text.strip()
                        if text:
                            # Don't split paragraph text — treat it as one chunk
                            chunked_doc = text_splitter_docx.create_documents([text])
                            for t in chunked_doc:
                                t.metadata['type'] = 'text'
                                docs.append(t)
                    elif isinstance(block, Table):
                        table_text = self.serialize_table(block)
                        if table_text:
                            docs.append(Document(page_content=table_text, metadata={"type": "table"}))
            else:
                loader = PyPDFLoader(tmp_file.name)
                pages = loader.load()
                for page in pages:
                    # Split page text
                    split_texts = text_splitter_pdf.split_text(page.page_content)
                    for t in split_texts:
                        docs.append(Document(page_content=t, metadata={"type": "text"}))
                    
            return docs

        
    def iter_block_items(self, parent):
        for child in parent.element.body.iterchildren():
            if child.tag.endswith('}p'):
                yield Paragraph(child, parent)
            elif child.tag.endswith('}tbl'):
                yield Table(child, parent)

    def serialize_table(self, table):
        rows = []
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            rows.append(" | ".join(cells))
        return "\n".join(rows)
    
    
       
    async def load_file_to_vectorstore(self, file_bytes, suffix, file_name):
        page_content = self.load_document_from_bytes(file_bytes, suffix)
        
        # return
        chunks = [doc.page_content for doc in page_content]
        # print("page_content::: ", chunks)
        embd_chunks = embeddings.embed_documents(chunks)

        records = [
                [
                    emb,
                    f""""
                    --------------- {file_name}--------------\n\n   

                    --------------------------------------\n\n
                    {meta.page_content}
                        \n
                    """,


                    file_name,
                    meta.metadata['source'] if "source" in meta.metadata else "",
                    meta.metadata['page'] if 'page' in meta.metadata else 0

                ]
                for emb, meta in zip(embd_chunks, page_content)
        ]
        # print("records::: ", records[0])
        # return
        vectors, texts, sources, web_links, pages = zip(*records)
        collection = Collection(setting.ZILLIS_COLLECTION_NAME)

        collection.insert([
            list(vectors),
            list(texts),
            list(sources),
            list(web_links),
            list(pages)
        ])
        
        
        