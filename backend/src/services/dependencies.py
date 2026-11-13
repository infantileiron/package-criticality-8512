import uuid
from fastapi import HTTPException
from sqlalchemy import select
from src.models import WorkPackage,TaskDependency
from src.services.validation import validate_package
from src.utils.serialization import serialize
from src.utils.time import now

def create(db,payload):
 package=db.scalar(select(WorkPackage).where(WorkPackage.id==payload.package_id).with_for_update())
 if not package:raise HTTPException(404,'工作包不存在')
 existing=list(db.scalars(select(TaskDependency).where(TaskDependency.package_id==payload.package_id)))
 if any(e.predecessor==payload.predecessor and e.successor==payload.successor for e in existing):raise HTTPException(409,'重复依赖')
 edges=[(e.predecessor,e.successor) for e in existing]+[(payload.predecessor,payload.successor)]
 try:validate_package(package.tasks,edges)
 except ValueError as e:raise HTTPException(422,str(e))
 item=TaskDependency(id=str(uuid.uuid4()),created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)
