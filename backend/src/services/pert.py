"""Beta-PERT(lambda=4) with optional shared stoppage events.

Legacy independent sampling is preserved exactly: when no events are configured
the duration RNG stream is identical to the original implementation.
"""
import math,random,statistics
from src.services.cpm import cpm,TOLERANCE

def _number(value):return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)

def validate_ranges(tasks):
 if not tasks or len({t['task_id'] for t in tasks})!=len(tasks):raise ValueError('unique tasks required')
 for t in tasks:
  a,m,b=t['a'],t['m'],t['b']
  if not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in (a,m,b)) or not 0<=a<=m<=b:raise ValueError('requires finite 0 <= a <= m <= b')
 return tasks

def normalize_events(events,task_ids=None):
 """Validate and normalize stoppage events; sorted by event_id for stable RNG order."""
 if events is None:return []
 if not isinstance(events,list):raise ValueError('停工事件须为列表')
 if len(events)>20:raise ValueError('停工事件最多20项')
 normalized=[];seen=set();known=set(task_ids) if task_ids is not None else None
 for event in events:
  if not isinstance(event,dict):raise ValueError('停工事件格式无效')
  event_id=event.get('event_id')
  if not isinstance(event_id,str) or not event_id or not event_id.isascii() or not event_id[0].isalpha() or not all(c.isalnum() or c in '_-' for c in event_id) or len(event_id)>24:raise ValueError('停工事件ID须为最多24位英数短ID')
  if event_id in seen:raise ValueError('停工事件ID须唯一')
  seen.add(event_id)
  name=event.get('name')
  if not isinstance(name,str) or not 1<=len(name)<=80:raise ValueError('停工事件名称须为1至80字')
  probability=event.get('probability')
  if not _number(probability) or not 0<=probability<=1:raise ValueError('停工事件发生概率须在0至1之间')
  delay=event.get('delay_hours')
  if not _number(delay) or delay<0 or delay>1000000:raise ValueError('停工事件固定延误须为0至1000000有限小时')
  task_list=event.get('task_ids')
  if not isinstance(task_list,list) or not 1<=len(task_list)<=60:raise ValueError('停工事件须关联1至60个任务')
  if not all(isinstance(t,str) and t for t in task_list) or len(set(task_list))!=len(task_list):raise ValueError('停工事件关联任务须为唯一非空任务ID')
  if known is not None and any(t not in known for t in task_list):raise ValueError('停工事件关联任务须存在于工作包')
  normalized.append({'event_id':event_id,'name':name,'probability':float(probability),'delay_hours':float(delay),'task_ids':sorted(task_list)})
 return sorted(normalized,key=lambda event:event['event_id'])

def quantile(sorted_values,q):
 position=(len(sorted_values)-1)*q;lo=math.floor(position);hi=math.ceil(position);return sorted_values[lo]+(sorted_values[hi]-sorted_values[lo])*(position-lo)

def simulate(tasks,edges,samples,seed,deadline,events=None):
 validate_ranges(tasks)
 if isinstance(samples,bool) or not isinstance(samples,int) or not 1<=samples<=10000:raise ValueError('invalid simulation sample count')
 if isinstance(seed,bool) or not isinstance(seed,int) or seed<0:raise ValueError('invalid seed')
 if not math.isfinite(deadline) or deadline<0:raise ValueError('invalid deadline')
 tasks=sorted(tasks,key=lambda t:t['task_id']);cpm({t['task_id']:t['m'] for t in tasks},edges)
 event_config=normalize_events(events,[t['task_id'] for t in tasks])
 rng=random.Random(seed);event_rng=random.Random(seed+1);finish=[];counts={t['task_id']:0 for t in tasks};ranges=[]
 event_counts={event['event_id']:0 for event in event_config};any_event=0
 for t in tasks:
  a,m,b=t['a'],t['m'],t['b'];alpha=None if a==b else 1+4*(m-a)/(b-a);beta=None if a==b else 1+4*(b-m)/(b-a)
  ranges.append({**t,'alpha':alpha,'beta':beta,'point_mass':a==b})
 for _ in range(samples):
  durations={t['task_id']:t['a'] if t['point_mass'] else t['a']+(t['b']-t['a'])*rng.betavariate(t['alpha'],t['beta']) for t in ranges}
  task_delay={};hit=False
  for event in event_config:
   if event_rng.random()<event['probability']:
    hit=True;event_counts[event['event_id']]+=1
    for task_id in event['task_ids']:task_delay[task_id]=task_delay.get(task_id,0.0)+event['delay_hours']
  if hit:any_event+=1
  for task_id,delay in task_delay.items():durations[task_id]+=delay
  run=cpm(durations,edges,TOLERANCE);finish.append(run['project_finish'])
  for row in run['tasks']:
   if row['critical']:counts[row['task_id']]+=1
 ordered=sorted(finish);on_time=sum(v<=deadline+TOLERANCE for v in finish);low,high=ordered[0],ordered[-1];width=(high-low)/18 if high>low else 0.;hist=[]
 if width:
  bins=[0]*18
  for value in finish:bins[min(17,int((value-low)/width))]+=1
  hist=[{'left':low+i*width,'right':low+(i+1)*width,'count':count} for i,count in enumerate(bins)]
 else:hist=[{'left':low,'right':high,'count':samples}]
 event_stats=[{**event,'occurrence_count':event_counts[event['event_id']],'denominator':samples,'occurrence_rate':event_counts[event['event_id']]/samples} for event in event_config]
 return {'samples':samples,'seed':seed,'deadline':deadline,'on_time_count':on_time,'deadline_tolerance_hours':TOLERANCE,'on_time_probability':on_time/samples,'mean_finish':statistics.fmean(finish),'quantiles':{'p05':quantile(ordered,.05),'p50':quantile(ordered,.5),'p80':quantile(ordered,.8),'p95':quantile(ordered,.95)},'finish_times':finish,'histogram':hist,'task_criticality':[{'task_id':t['task_id'],'critical_count':counts[t['task_id']],'denominator':samples,'criticality':counts[t['task_id']]/samples} for t in tasks],'ranges':ranges,'lambda':4,'tolerance_hours':TOLERANCE,'quantile_method':'linear interpolation at (n-1)*q','independence_assumption':not event_config,'event_model':'shared_stoppage_events' if event_config else 'independent_durations','events':event_stats,'event_any_count':any_event,'event_any_rate':any_event/samples}
