


def get_all_functions():
        r = [
            {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "获取城市天气信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "城市名，如北京"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
        ]
        return r

def get_weather(location: str) -> str:
    return f"当前 {location} 晴天，温度 25°C"



import inspect
import json
from typing import Dict, Callable, List, Any

class BaseTool:
    registry: Dict[str, Callable] = {}

    @classmethod
    def get_tools(cls) -> List[Dict[str, Any]]:
        tools = []
        for name, fn in cls.registry.items():
            sig = inspect.signature(fn)
            parameters = {
                "type": "object",
                "properties": {},
                "required": [],
            }
            for param in sig.parameters.values():
                parameters["properties"][param.name] = {
                    "type": "string",  # 可根据需要支持其他类型
                    "description": f"{param.name} 参数"
                }
                parameters["required"].append(param.name)

            tools.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": fn.__doc__ or "无描述",
                    "parameters": parameters
                }
            })
        return tools

    @classmethod
    def call(cls, name: str, args: Dict[str, Any]) -> str:
        if name not in cls.registry:
            raise ValueError(f"工具 {name} 未注册")
        return cls.registry[name](**args)

    @classmethod
    def register(cls, fn: Callable):
        cls.registry[fn.__name__] = fn
        return fn
    
    @classmethod
    async def acall(cls, name: str, args: Dict[str, Any]) -> str:
        result = cls.call(name, args)
        # 如果需要支持真正的异步函数，可以检测是否是协程函数
        if inspect.iscoroutine(result):
            return await result
        return result

class MyTools(BaseTool):
    
    @BaseTool.register
    def get_weather(location: str) -> str:
        """获取天气"""
        return f"{location} 今天晴，25°C。"

    @BaseTool.register
    def get_time(city: str) -> str:
        """获取时间"""
        return f"{city} 当前时间是 12:00"