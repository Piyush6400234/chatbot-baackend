from fastapi import APIRouter, File, UploadFile, Response, status
import warnings
from src.vectorstore.milvus_connect import MilvusStore
from .model import ChatQuestion
from src.llms.Azure import Azurellm
from src.prompts.prompt import prompt_dict
from src.app.config import setting

router = APIRouter()

warnings.filterwarnings("ignore")

@router.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):

    content = await file.read()
    suffix = f".{file.filename.split('.')[-1]}" if '.' in file.filename else ""
    milvusClient = MilvusStore()
    documents = await milvusClient.load_file_to_vectorstore(content, suffix=suffix, file_name=file.filename)
    
    
    return {"success": "ok"}


@router.options("/chat/")
async def options_handler(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return Response(status_code=status.HTTP_200_OK)

@router.post("/chat/")
async def upload_file(request: ChatQuestion, response:Response):
    vectorStore = MilvusStore()
    vectorCollection = await vectorStore.get_vectorstore(collection_name=setting.ZILLIS_COLLECTION_NAME)
    docs = await vectorStore.search_vectorStore(request.query, vectorCollection)
    context = ' '


    for i in docs:
        context = context + i[0].page_content
    
    input_data = {
        "question": request.query,
        "context": context
    }
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    result = Azurellm()
    result = await result.retrieve_answer_using_llm(input_data, prompt_dict)
    return {"res": result.content}






    