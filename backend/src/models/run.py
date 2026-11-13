from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class ScheduleRun(Base):
 __tablename__='schedule_runs'
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 scenario_id:Mapped[str]=mapped_column(ForeignKey('duration_scenarios.id'))
 status:Mapped[str]=mapped_column(String(32))
 result:Mapped[dict]=mapped_column(JSON,default=dict)
 error:Mapped[str]=mapped_column(Text,default='')
 created_at:Mapped[str]=mapped_column(String(64))
