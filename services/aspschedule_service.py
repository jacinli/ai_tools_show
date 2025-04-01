import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScheduleService:
    def __init__(self):
        self.fixed_times = ["08:00", "12:00", "18:00"]  # 固定调度时间列表
        self.scheduler = AsyncIOScheduler()

    async def fixed_task(self):
        logger.info("[定时任务] ✅ 执行固定时间任务逻辑")
        # TODO: 这里是你的异步业务逻辑
        await asyncio.sleep(1)  # 模拟异步操作
        logger.info("[定时任务] ✅ 执行完成")

    def add_jobs(self):
        for time_str in self.fixed_times:
            hour, minute = map(int, time_str.split(":"))
            self.scheduler.add_job(self._wrap_async(self.fixed_task), CronTrigger(hour=hour, minute=minute))
            logger.info(f"[调度器] 已添加定时任务: 每天 {hour:02d}:{minute:02d}")

    def _wrap_async(self, coro_func):
        """封装异步函数为 APScheduler 可调度的同步函数"""
        def wrapper():
            asyncio.create_task(coro_func())
        return wrapper

    def start(self):
        self.add_jobs()
        self.scheduler.start()


if __name__ == "__main__":
    service = ScheduleService()
    service.start()
    logger.info("[服务启动] Scheduler 已启动")
    asyncio.get_event_loop().run_forever()
