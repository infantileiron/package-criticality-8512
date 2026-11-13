from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class DurationScenario(Base):
 __tablename__='duration_scenarios'
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 name:Mapped[str]=mapped_column(String(160),unique=True)
 package_id:Mapped[str]=mapped_column(ForeignKey('work_packages.id'))
 version:Mapped[int]=mapped_column(Integer)
 deadline:Mapped[float]=mapped_column(Double)
 samples:Mapped[int]=mapped_column(Integer)
 seed:Mapped[int]=mapped_column(Integer)
 snapshot:Mapped[dict]=mapped_column(JSON)
 created_at:Mapped[str]=mapped_column(String(64))
