from pydantic import BaseModel,Field,ConfigDict
from typing import Literal
class DependencyInput(BaseModel):
 model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
 package_id:str
 predecessor:str
 successor:str
