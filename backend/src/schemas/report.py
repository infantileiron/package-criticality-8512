from pydantic import BaseModel,Field,ConfigDict
from typing import Literal
class ReportInput(BaseModel):
 model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
 run_id:str
 title:str=Field(min_length=2,max_length=180)
