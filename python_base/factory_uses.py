from typing import Dict, Callable, Any
import inspect
import json

# 工具工厂基类
class BaseTool:
    registry: Dict[str, Callable] = {}

    @classmethod
    def register(cls, fn: Callable):
        """注册工具函数到工厂"""
        cls.registry[fn.__name__] = fn
        return fn

    @classmethod
    def get_tools(cls):
        """返回所有注册的工具定义（给 OpenAI）"""
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
                    "type": "string",
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
        """根据名称调用工具函数"""
        if name not in cls.registry:
            raise ValueError(f"未注册的工具函数: {name}")
        return cls.registry[name](**args)

# ==============================

# 子类工具集：自动注册
class MyTools(BaseTool):

    @BaseTool.register
    def get_weather(location: str) -> str:
        """获取城市天气信息"""
        return f"☀️ 当前 {location} 晴天，温度 25°C"

    @BaseTool.register
    def get_time(city: str) -> str:
        """获取当前时间"""
        return f"🕒 当前 {city} 时间为 12:00"

# ==============================

# 🧪 测试工厂调用
if __name__ == "__main__":
    tools = BaseTool.get_tools()
    print("注册的工具定义（可传给 OpenAI 的 tools）:")
    print(json.dumps(tools, indent=2, ensure_ascii=False))

    print("\n✅ 工厂调用 get_weather:")
    result = BaseTool.call("get_weather", {"location": "北京"})
    print(result)

    print("\n✅ 工厂调用 get_time:")
    result = BaseTool.call("get_time", {"city": "上海"})
    print(result)