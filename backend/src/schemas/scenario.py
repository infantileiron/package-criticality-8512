from pydantic import BaseModel,Field,ConfigDict
class StoppageEventInput(BaseModel):
 model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
 event_id:str=Field(min_length=1,max_length=24)
 name:str=Field(min_length=1,max_length=80)
 probability:float=Field(ge=0,le=1)
 delay_hours:float=Field(ge=0,le=1000000)
 task_ids:list[str]=Field(min_length=1,max_length=60)
class ScenarioInput(BaseModel):
 model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
 name:str=Field(min_length=2,max_length=160)
 package_id:str
 deadline:float=Field(ge=0,le=1000000)
 samples:int=Field(ge=100,le=5000,strict=True)
 seed:int=Field(ge=0,le=2147483647,strict=True)
 events:list[StoppageEventInput]=Field(default_factory=list,max_length=20)
