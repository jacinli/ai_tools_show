from openai import  AsyncOpenAI
from dotenv import load_dotenv
import os
import json
from services.openai_tools_call import get_all_functions
from services.openai_tools_call import get_weather,MyTools,BaseTool
load_dotenv()


class AsyncOpenAIOut:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL")
        self.oai_client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        self.model = os.getenv("OPENAI_MODEL")
    

    async def gpt_stream_with_tools(self, user_message: str, model: str = None, history: list[dict] = [], system_prompt: str = ""):
        functions = get_all_functions()
        # functions = MyTools.get_tools()
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        # 第一次调用，检查是否触发函数调用
        response = await self.oai_client.chat.completions.create(
            model=model or self.model,
            messages=messages,
            tools=functions,
            tool_choice="auto"
        )

        choice = response.choices[0]

        # 如果有 tool 调用
        if choice.message.tool_calls:
            for tool_call in choice.message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f"函数调用: {name} 参数: {args}")

                # 执行本地函数（你定义的 get_weather）
                if name == "get_weather":
                    result = get_weather(**args)

                    # 添加 assistant 的 tool_calls 回复
                    messages.append({
                        "role": "assistant",
                        "tool_calls": [{
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": name,
                                "arguments": json.dumps(args)
                            }
                        }]
                    })

                    # 添加 tool 执行结果
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })

                    # 重新调用一次 OpenAI，得到最终结果
                    second_response = await self.oai_client.chat.completions.create(
                        model=model or self.model,
                        messages=messages,
                        stream=True
                    )

                    async for chunk in second_response:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
        else:
            # 没有触发函数调用，正常输出
            if choice.message.content:
                yield choice.message.content


    async def gpt_stream_with_tools_for_base_tool(self, user_message: str, model: str = None, history: list[dict] = [], system_prompt: str = ""):

        tools = MyTools.get_tools()  # 获取所有 tools 结构
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        # 第一次调用，检查是否触发函数调用
        response = await self.oai_client.chat.completions.create(
            model=model or self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        choice = response.choices[0]

        # 如果触发 tool 调用
        if choice.message.tool_calls:
            for tool_call in choice.message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f"函数调用: {name} 参数: {args}")

                # 自动调度工具
                result = await BaseTool.acall(name, args)  # 异步支持

                # 添加 assistant 工具调用记录
                messages.append({
                    "role": "assistant",
                    "tool_calls": [{
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": name,
                            "arguments": json.dumps(args)
                        }
                    }]
                })

                # 添加 tool 执行结果
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

            # 再次请求模型以获得最终回复
            second_response = await self.oai_client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                stream=True
            )

            async for chunk in second_response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        else:
            if choice.message.content:
                yield choice.message.content
    async def gpt_stream(self, user_message: str,model: str = os.getenv("OPENAI_MODEL"),history: list[dict] = [],system_prompt: str = "") :
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
        async for chunk in async_openai_out.gpt_stream_with_tools_for_base_tool(user_message="北京的时间多少？",system_prompt="You are a helpful assistant."):
            # print(chunk)
            await asyncio.to_thread(print, chunk)  # 在后台线程执行 print

    import asyncio
    
    asyncio.run(test_gpt_stream())

