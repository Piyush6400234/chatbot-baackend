from langchain_community.vectorstores.milvus import Milvus
from src.app.config import setting
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from docx import Document as Documentx
from langchain_community.embeddings import AzureOpenAIEmbeddings
from io import BytesIO
import tempfile
from pymilvus import connections, Collection
import os




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
        return await vector_store.asimilarity_search_with_score(query, k=100)



    async def load_doc_to_milvus(self, docs):
        vectorstore = await self.get_vectorstore(setting.ZILLIS_COLLECTION_NAME)
        await vectorstore.add_texts(docs)

        
    def load_document_from_bytes(self, file_bytes, suffix):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(file_bytes)

            tmp_file.flush()
            
            # Use the path of the temporary file for PyPDFLoader
            if suffix == ".docx":
                doc = Documentx(BytesIO(file_bytes))
                full_text = "\n".join([para.text for para in doc.paragraphs])
                pages = text_splitter.create_documents([full_text])
            else:
                loader = PyPDFLoader(tmp_file.name)
                pages = loader.load_and_split()
                pages = text_splitter.split_documents(pages)
                
            
            
            return pages

        
    async def load_file_to_vectorstore(self, file_bytes, suffix, file_name):
        page_content = self.load_document_from_bytes(file_bytes, suffix)

        chunks = [doc.page_content for doc in page_content]
        embd_chunks = embeddings.embed_documents(chunks)

        records = [
                [
                    emb,
                    f""""file Name: {file_name}\n\n +{meta.page_content}""",
                    file_name,
                    meta.metadata['source'] if "source" in meta.metadata else "",
                    meta.metadata['page'] if 'page' in meta.metadata else 0

                ]
                for emb, meta in zip(embd_chunks, page_content)
        ]

        vectors, texts, sources, web_links, pages = zip(*records)
        collection = Collection(setting.ZILLIS_COLLECTION_NAME)

        collection.insert([
            list(vectors),
            list(texts),
            list(sources),
            list(web_links),
            list(pages)
        ])
        
        
        
        
