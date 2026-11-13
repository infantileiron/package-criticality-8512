from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class WorkPackage(Base):
 __tablename__='work_packages'
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 name:Mapped[str]=mapped_column(String(160),unique=True)
 source:Mapped[str]=mapped_column(String(180))
 tasks:Mapped[list]=mapped_column(JSON)
 created_at:Mapped[str]=mapped_column(String(64))
