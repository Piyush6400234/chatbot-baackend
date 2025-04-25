from langchain.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
import httpx
from src.app.config import setting

llm = AzureChatOpenAI(
    api_key = setting.AZURE_OPENAI_LLM_KEY,
    azure_deployment = "gpt-4o",
    model = "gpt-4o",
    api_version="2024-12-01-preview",
    azure_endpoint=setting.AZURE_OPENAI_LLM_ENDPOINT,
    temperature=0,
    request_timeout=httpx.Timeout(20.0),
    max_retries=5,
    streaming=True
)



class Azurellm:
    def __init__(self):
        pass
    
    async def retrieve_answer_using_llm(self, input_data, prompt_dict):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",  prompt_dict["system_prompt"]
                ),
                (
                    "user", prompt_dict["user_prompt"]
                )
            ]

        )

        text = prompt.format_messages(context=input_data["context"], question=input_data["question"])

        
        print("text:: ", text)




        response = await llm.ainvoke(text)

        return response














