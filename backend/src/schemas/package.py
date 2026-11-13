from pydantic import BaseModel,Field,ConfigDict
class TaskInput(BaseModel):
 model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
 task_id:str
 name:str=Field(min_length=1,max_length=80)
 a:float=Field(ge=0)
 m:float=Field(ge=0)
 b:float=Field(ge=0)
class PackageInput(BaseModel):
 model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
 name:str=Field(min_length=2,max_length=160)
 source:str=Field(min_length=2,max_length=180)
 tasks:list[TaskInput]=Field(min_length=1,max_length=60)
