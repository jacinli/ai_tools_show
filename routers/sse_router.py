from fastapi import FastAPI,Request,Response
from fastapi.responses import StreamingResponse
from services.async_openai_out import async_openai_out
import asyncio
import json
app = FastAPI()


@app.post('/sse/v1')
async def root(request: Request):
    async def event_stream():
        for i in range(10):
            yield f"data: {i}\n\n"
            await asyncio.sleep(0.1)
    r = StreamingResponse(event_stream(), media_type="text/event-stream")
    return r

@app.post('/sse/no_sse')
async def root(request: Request):
    r = {"message": "Hello World"} # 也可以直接返回return r
    return Response(content=json.dumps(r), media_type="application/json")

@app.post("/sse/async_openai_out")
async def root(request: Request):
    user_message = "你好"
    async def gpt_stream():
        async for chunk in async_openai_out.gpt_stream(user_message=user_message,system_prompt="You are a helpful assistant."):
            print(chunk)
            yield f'data: {chunk}\n\n'
    r = StreamingResponse(gpt_stream(), media_type="text/event-stream")
    return r
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
