"""Zero-lag finish-start DAG; virtual source/sink implemented by common bounds."""
import math,heapq
TOLERANCE=1e-8

def cpm(durations,edges,tolerance=TOLERANCE):
 if not durations:raise ValueError('at least one task required')
 if not math.isfinite(tolerance) or tolerance<0:raise ValueError('invalid tolerance')
 if not all(isinstance(k,str) and k for k in durations):raise ValueError('task IDs must be nonempty strings')
 if not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and v>=0 for v in durations.values()):raise ValueError('task durations must be finite nonnegative hours')
 ids=sorted(durations);pred={k:[] for k in ids};succ={k:[] for k in ids};seen=set()
 for edge in edges:
  if len(edge)!=2:raise ValueError('dependency requires predecessor and successor')
  a,b=edge
  if a not in durations or b not in durations:raise ValueError('unknown dependency endpoint')
  if a==b or (a,b) in seen:raise ValueError('self-loop or duplicate dependency')
  seen.add((a,b));succ[a].append(b);pred[b].append(a)
 degree={k:len(pred[k]) for k in ids};heap=[k for k in ids if not degree[k]];heapq.heapify(heap);order=[]
 while heap:
  k=heapq.heappop(heap);order.append(k)
  for j in sorted(succ[k]):
   degree[j]-=1
   if degree[j]==0:heapq.heappush(heap,j)
 if len(order)!=len(ids):raise ValueError('dependency graph contains a cycle')
 es={};ef={}
 for k in order:
  es[k]=max((ef[j] for j in pred[k]),default=0.0);ef[k]=es[k]+durations[k]
 finish=max(ef.values());ls={};lf={}
 if not math.isfinite(finish):raise ValueError('project finish overflow')
 for k in reversed(order):
  lf[k]=min((ls[j] for j in succ[k]),default=finish);ls[k]=lf[k]-durations[k]
 rows=[]
 for k in ids:
  slack=ls[k]-es[k]
  if abs(slack)<=tolerance:slack=0.0
  rows.append({'task_id':k,'duration':durations[k],'es':es[k],'ef':ef[k],'ls':ls[k],'lf':lf[k],'total_float':slack,'critical':slack<=tolerance,'predecessors':sorted(pred[k]),'successors':sorted(succ[k])})
 critical={r['task_id'] for r in rows if r['critical']};critical_edges=[list(e) for e in sorted(seen) if e[0] in critical and e[1] in critical and abs(ef[e[0]]-es[e[1]])<=tolerance]
 return {'project_finish':finish,'tasks':rows,'topological_order':order,'critical_tasks':sorted(critical),'critical_edges':critical_edges,'tolerance_hours':tolerance,'virtual_source_tasks':[k for k in ids if not pred[k]],'virtual_sink_tasks':[k for k in ids if not succ[k]],'lf_basis':'actual project finish; external deadline never used'}
