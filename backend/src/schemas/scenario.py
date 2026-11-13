from pydantic import BaseModel,Field,ConfigDict
from typing import Literal
class ScenarioInput(BaseModel):
 model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
 name:str=Field(min_length=2,max_length=160)
 package_id:str
 deadline:float=Field(ge=0,le=1000000)
 samples:int=Field(ge=100,le=5000,strict=True)
 seed:int=Field(ge=0,le=2147483647,strict=True)
