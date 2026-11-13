import uuid
from fastapi import HTTPException
from sqlalchemy import select
from src.models import WorkPackage
from src.services.validation import validate_package
from src.utils.serialization import serialize
from src.utils.time import now

def create(db,payload):
 data=payload.model_dump()
 try:validate_package(data['tasks'])
 except ValueError as e:raise HTTPException(422,str(e))
 if db.scalar(select(WorkPackage).where(WorkPackage.name==payload.name)):raise HTTPException(409,'工作包名称已存在')
 item=WorkPackage(id=str(uuid.uuid4()),created_at=now(),**data);db.add(item);db.commit();return serialize(item)
