import uuid,redis
from fastapi import HTTPException
from src.models import ScheduleRun,DurationScenario
from src.config.settings import REDIS_URL
from src.utils.serialization import serialize
from src.utils.time import now

def create(db,scenario_id):
 if not db.get(DurationScenario,scenario_id):raise HTTPException(404,'风险情景不存在')
 item=ScheduleRun(id=str(uuid.uuid4()),scenario_id=scenario_id,status='queued',result={},error='',created_at=now());db.add(item);db.commit()
 try:redis.Redis.from_url(REDIS_URL).lpush('package-criticality:jobs',item.id)
 except redis.RedisError:
  item.status='failed';item.error='后台队列不可用，请重试';db.commit();raise HTTPException(503,item.error)
 return serialize(item)
def require_completed(db,id):
 run=db.get(ScheduleRun,id)
 if not run:raise HTTPException(404,'运行不存在')
 if run.status!='completed':raise HTTPException(409,'风险计算尚未完成')
 return run
