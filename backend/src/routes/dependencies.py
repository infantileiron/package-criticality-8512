from fastapi import APIRouter,Depends,HTTPException,Response
from sqlalchemy import select
from src.config.database import db_session
from src.controllers.auth import current_user,writer,admin
from src.models import TaskDependency
from src.schemas.dependency import DependencyInput
from src.services import dependencies as service
from src.utils.serialization import rows,serialize
router=APIRouter(prefix='/dependencies')
@router.get('')
def listing(db=Depends(db_session),user=Depends(current_user)):return rows(db.scalars(select(TaskDependency).order_by(TaskDependency.created_at.desc())))
@router.post('')
def create(payload:DependencyInput,db=Depends(db_session),user=Depends(writer)):return service.create(db,payload)
