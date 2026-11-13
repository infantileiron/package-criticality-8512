import uuid
from fastapi import HTTPException
from sqlalchemy import select,func
from src.models import WorkPackage,TaskDependency,DurationScenario
from src.utils.serialization import serialize
from src.utils.time import now

def create(db,payload):
 package=db.scalar(select(WorkPackage).where(WorkPackage.id==payload.package_id).with_for_update())
 if not package:raise HTTPException(404,'工作包不存在')
 if db.scalar(select(DurationScenario).where(DurationScenario.name==payload.name)):raise HTTPException(409,'风险情景名称已存在')
 edges=list(db.scalars(select(TaskDependency).where(TaskDependency.package_id==package.id).order_by(TaskDependency.predecessor,TaskDependency.successor)))
 version=(db.scalar(select(func.max(DurationScenario.version)).where(DurationScenario.package_id==package.id)) or 0)+1
 item=DurationScenario(id=str(uuid.uuid4()),version=version,snapshot={'package':serialize(package),'dependencies':[serialize(e) for e in edges]},created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)
