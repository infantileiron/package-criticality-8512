from fastapi import APIRouter,Depends,HTTPException,Response
from sqlalchemy import select
from src.config.database import db_session
from src.controllers.auth import current_user,writer,admin
from src.models import WorkPackage
from src.schemas.package import PackageInput
from src.services import packages as service
from src.utils.serialization import rows,serialize
router=APIRouter(prefix='/packages')
@router.get('')
def listing(db=Depends(db_session),user=Depends(current_user)):return rows(db.scalars(select(WorkPackage).order_by(WorkPackage.created_at.desc())))
@router.post('')
def create(payload:PackageInput,db=Depends(db_session),user=Depends(writer)):return service.create(db,payload)
