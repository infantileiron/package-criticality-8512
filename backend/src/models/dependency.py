from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class TaskDependency(Base):
 __tablename__='task_dependencies'
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 __table_args__=(UniqueConstraint('package_id','predecessor','successor'),)
 package_id:Mapped[str]=mapped_column(ForeignKey('work_packages.id'))
 predecessor:Mapped[str]=mapped_column(String(32))
 successor:Mapped[str]=mapped_column(String(32))
 created_at:Mapped[str]=mapped_column(String(64))
