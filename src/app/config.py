from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
load_dotenv(override=True)


class Settings(BaseSettings):
    
    
    
    ZILLIS_ENDPOINT: str = os.environ.get('ZILLIS_ENDPOINT')
    ZILLIS_TOKEN: str = os.environ.get('ZILLIS_TOKEN')
    ZILLIS_COLLECTION_NAME: str = os.environ.get('ZILLIS_COLLECTION_NAME')
    
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = os.environ.get('AZURE_OPENAI_EMBEDDING_DEPLOYMENT')
    AZURE_OPENAI_API_KEY: str = os.environ.get('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT: str = os.environ.get('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_VERSION: str = os.environ.get('AZURE_OPENAI_API_VERSION')
    AZURE_OPENAI_API_TYPE: str = os.environ.get('AZURE_OPENAI_API_TYPE')
    
    AZURE_OPENAI_LLM_KEY: str = os.environ.get('AZURE_OPENAI_LLM_KEY')
    AZURE_OPENAI_LLM_ENDPOINT: str = os.environ.get('AZURE_OPENAI_LLM_ENDPOINT')



    
    ALLOWED_MIME_TYPES: dict = {
        'text/plain': '.txt',
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'application/json': '.json'
    }

setting = Settings()