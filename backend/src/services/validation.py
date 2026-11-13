import re
from src.services.pert import validate_ranges
from src.services.cpm import cpm

def validate_package(tasks,edges=()):
 if not 1<=len(tasks)<=60:raise ValueError('工作包须包含1至60任务')
 for t in tasks:
  if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,23}',t['task_id']):raise ValueError('任务ID须为唯一英数短ID')
 validate_ranges(tasks);return cpm({t['task_id']:t['m'] for t in tasks},edges)
