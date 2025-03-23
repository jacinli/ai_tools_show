from langfuse import Langfuse
import os
from functools import wraps

class LangfuseService:
    def __init__(self):
        self.langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST")
        )

    def trace_langfuse_generator(self, name="default-trace", user_id="anonymous"):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                trace = self.langfuse.trace(name=name, user_id=user_id)
                span = trace.span(name=func.__name__)
                try:
                    async for chunk in func(*args, **kwargs):
                        yield chunk
                    span.end()
                except Exception as e:
                    span.end(output=f"Error: {str(e)}")
                    raise
            return wrapper
        return decorator
        
    
langfuse_service = LangfuseService()