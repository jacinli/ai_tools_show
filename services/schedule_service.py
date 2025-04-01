import asyncio
import logging
import os
from datetime import datetime, timedelta

import redis.asyncio as redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScheduleService:
    def __init__(self):
        self.redis_subscribe_key = "demo:subscription"
        self.exist_subscribe_key = "demo:exist_push"
        self.push_interval_seconds = 600  # 推送间隔时间
        self.fixed_times = ["08:00", "12:00", "18:00"]  # 固定调度时间列表

    def get_next_run_time(self):
        now_time = datetime.now()
        today_str = now_time.strftime("%Y-%m-%d")
        
        # 今日的所有调度时间点
        run_times = [datetime.strptime(f"{today_str} {t}", "%Y-%m-%d %H:%M") for t in self.fixed_times]
        future_times = [t for t in run_times if t > now_time]

        if future_times:
            return min(future_times)
        else:
            # 如果今天已经过了所有调度时间，则返回明天的第一个时间点
            next_day = (now_time + timedelta(days=1)).strftime('%Y-%m-%d')
            return datetime.strptime(f"{next_day} {self.fixed_times[0]}", "%Y-%m-%d %H:%M")

    async def redis_client(self):
        return await redis.from_url("redis://localhost:6379", decode_responses=True)

    async def fixed_time_task(self):
        while True:
            next_run_time = self.get_next_run_time()
            sleep_seconds = max(1, (next_run_time - datetime.now()).total_seconds())
            logger.info(f"[定时任务] 下次执行时间: {next_run_time}, sleep {sleep_seconds:.0f} 秒")

            await asyncio.sleep(sleep_seconds)
            logger.info("[定时任务] 执行具体逻辑...✅")
            # TODO: 添加你自己的定时任务逻辑

    async def check_redis_and_push(self):
        while True:
            try:
                redis = await self.redis_client()
                now_score = int(datetime.now().strftime("%H%M"))
                trigger_score = now_score + 4

                subscriptions = await redis.zrangebyscore(
                    self.redis_subscribe_key, now_score, trigger_score, withscores=True
                )

                if subscriptions:
                    logger.info(f"[推送检查] 检测到 {len(subscriptions)} 条订阅")
                    for sub_key, _ in subscriptions:
                        user_id, tag = self.parse_key(sub_key)
                        push_key = f"{self.exist_subscribe_key}:{user_id}|{tag}"

                        if not await redis.exists(push_key):
                            logger.info(f"[推送中] 推送消息给用户 {user_id}，标签：{tag}")
                            # TODO: 实际的推送逻辑
                            await redis.setex(push_key, self.push_interval_seconds, "1")

                await redis.aclose()
            except Exception as e:
                logger.error(f"[推送异常] {str(e)}")

            await asyncio.sleep(60)

    def parse_key(self, key):
        """解析订阅键 user:xxx|tag:xxx"""
        try:
            parts = key.split("|")
            user_id = parts[0].split(":")[1]
            tag = parts[1].split(":")[1]
            return user_id, tag
        except Exception as e:
            logger.error(f"解析 key 失败: {key} -> {e}")
            return "", ""


if __name__ == "__main__":
    async def main():
        service = ScheduleService()
        await asyncio.gather(
            service.fixed_time_task(),
            service.check_redis_and_push(),
        )

    asyncio.run(main())
