from pydantic import BaseModel,Field,ConfigDict
from typing import Literal
class RunInput(BaseModel):
 model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
 scenario_id:str
