from openai import  AsyncOpenAI
from dotenv import load_dotenv
import os

load_dotenv()


class AsyncOpenAIOut:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL")
        self.oai_client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    async def gpt_stream(self, user_message: str,model: str = "gpt-4o-mini",history: list[dict] = [],system_prompt: str = "") :
        messages = []
        if history:
            messages.extend(history)
        
        if system_prompt:
            messages.extend([{"role": "system", "content": system_prompt}])
        
        messages.append({"role": "user", "content": user_message})
        response = await self.oai_client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

async_openai_out = AsyncOpenAIOut()




if __name__ == "__main__":
    async def test_gpt_stream():
        async for chunk in async_openai_out.gpt_stream(user_message="写300字作文",system_prompt="You are a helpful assistant."):
            print(chunk)

    import asyncio
    
    asyncio.run(test_gpt_stream())

