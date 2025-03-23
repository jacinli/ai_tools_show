
import asyncio
import time
import threading

async def test_async():
    async def say_hello(delay:int=1,name:str="world"):
        if delay == 1:
            await asyncio.sleep(20)
        await asyncio.sleep(delay)
        print(f"hello {name}")
    
    task1 = asyncio.create_task(say_hello(1,"world-1"))
    task2 = asyncio.create_task(say_hello(2,"world-2"))
    task3 = asyncio.create_task(say_hello(3,"world-3"))
    
    await task1
    await task2
    await task3
    await say_hello(1,"world-100")
    await say_hello(2,"world-200")
    await say_hello(3,"world-300")





if __name__ == "__main__":
    asyncio.run(test_async())