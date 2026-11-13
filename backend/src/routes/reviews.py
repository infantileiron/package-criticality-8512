from fastapi import APIRouter,Depends,HTTPException,Response
from sqlalchemy import select
from src.config.database import db_session
from src.controllers.auth import current_user,writer,admin
from src.models import DeliveryReview
from src.schemas.review import ReviewInput
from src.services import reviews as service
from src.utils.serialization import rows,serialize
router=APIRouter(prefix='/reviews')
@router.get('')
def listing(db=Depends(db_session),user=Depends(current_user)):return rows(db.scalars(select(DeliveryReview).order_by(DeliveryReview.created_at.desc())))
@router.post('')
def create(payload:ReviewInput,db=Depends(db_session),user=Depends(writer)):return service.create(db,payload,user)
