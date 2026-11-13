"""Independent Beta-PERT(lambda=4), deterministic stdlib RNG, fresh CPM per draw."""
import math,random,statistics
from src.services.cpm import cpm,TOLERANCE

def validate_ranges(tasks):
 if not tasks or len({t['task_id'] for t in tasks})!=len(tasks):raise ValueError('unique tasks required')
 for t in tasks:
  a,m,b=t['a'],t['m'],t['b']
  if not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in (a,m,b)) or not 0<=a<=m<=b:raise ValueError('requires finite 0 <= a <= m <= b')
 return tasks

def quantile(sorted_values,q):
 position=(len(sorted_values)-1)*q;lo=math.floor(position);hi=math.ceil(position);return sorted_values[lo]+(sorted_values[hi]-sorted_values[lo])*(position-lo)

def simulate(tasks,edges,samples,seed,deadline):
 validate_ranges(tasks)
 if isinstance(samples,bool) or not isinstance(samples,int) or not 1<=samples<=10000:raise ValueError('invalid simulation sample count')
 if isinstance(seed,bool) or not isinstance(seed,int) or seed<0:raise ValueError('invalid seed')
 if not math.isfinite(deadline) or deadline<0:raise ValueError('invalid deadline')
 tasks=sorted(tasks,key=lambda t:t['task_id']);cpm({t['task_id']:t['m'] for t in tasks},edges)
 rng=random.Random(seed);finish=[];counts={t['task_id']:0 for t in tasks};ranges=[]
 for t in tasks:
  a,m,b=t['a'],t['m'],t['b'];alpha=None if a==b else 1+4*(m-a)/(b-a);beta=None if a==b else 1+4*(b-m)/(b-a)
  ranges.append({**t,'alpha':alpha,'beta':beta,'point_mass':a==b})
 for _ in range(samples):
  durations={t['task_id']:t['a'] if t['point_mass'] else t['a']+(t['b']-t['a'])*rng.betavariate(t['alpha'],t['beta']) for t in ranges}
  run=cpm(durations,edges,TOLERANCE);finish.append(run['project_finish'])
  for row in run['tasks']:
   if row['critical']:counts[row['task_id']]+=1
 ordered=sorted(finish);on_time=sum(v<=deadline+TOLERANCE for v in finish);low,high=ordered[0],ordered[-1];width=(high-low)/18 if high>low else 0.;hist=[]
 if width:
  bins=[0]*18
  for value in finish:bins[min(17,int((value-low)/width))]+=1
  hist=[{'left':low+i*width,'right':low+(i+1)*width,'count':count} for i,count in enumerate(bins)]
 else:hist=[{'left':low,'right':high,'count':samples}]
 return {'samples':samples,'seed':seed,'deadline':deadline,'on_time_count':on_time,'deadline_tolerance_hours':TOLERANCE,'on_time_probability':on_time/samples,'mean_finish':statistics.fmean(finish),'quantiles':{'p05':quantile(ordered,.05),'p50':quantile(ordered,.5),'p80':quantile(ordered,.8),'p95':quantile(ordered,.95)},'finish_times':finish,'histogram':hist,'task_criticality':[{'task_id':t['task_id'],'critical_count':counts[t['task_id']],'denominator':samples,'criticality':counts[t['task_id']]/samples} for t in tasks],'ranges':ranges,'lambda':4,'tolerance_hours':TOLERANCE,'quantile_method':'linear interpolation at (n-1)*q','independence_assumption':True}
