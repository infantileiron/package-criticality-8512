"""Stoppage-event (common-cause delay) regression tests.

Run from the repository root: python -m unittest discover -s test-artifacts/gb-2410 -p 'test_*.py' -v
"""
import math,os,random,sys,unittest
BACKEND=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),'backend')
sys.path.insert(0,BACKEND)
from src.services.pert import normalize_events,simulate
from src.services.analysis import analyze

TASKS=[{'task_id':'A','name':'交接','a':1.0,'m':2.0,'b':4.0},
       {'task_id':'B','name':'加固','a':2.0,'m':3.0,'b':6.0},
       {'task_id':'C','name':'复检','a':1.0,'m':1.0,'b':1.0},
       {'task_id':'FREE','name':'备件','a':0.0,'m':1.0,'b':2.0}]
EDGES=[('A','B'),('B','C')]
TASK_IDS=[t['task_id'] for t in TASKS]

class IndependentBaseline(unittest.TestCase):
 def test_no_events_keeps_independent_model(self):
  result=simulate(TASKS,EDGES,300,2410,10.)
  self.assertTrue(result['independence_assumption'])
  self.assertEqual(result['event_model'],'independent_durations')
  self.assertEqual(result['events'],[])
  self.assertEqual(result['event_any_count'],0)
  self.assertEqual(result['event_any_rate'],0)

 def test_p_zero_event_does_not_change_finish_times(self):
  base=simulate(TASKS,EDGES,300,7,10.)
  zero=simulate(TASKS,EDGES,300,7,10.,[{'event_id':'Z','name':'零概率','probability':0.,'delay_hours':9.,'task_ids':['A']}])
  self.assertEqual(base['finish_times'],zero['finish_times'])
  self.assertEqual(zero['events'][0]['occurrence_count'],0)

 def test_reordered_tasks_and_edges_reproduce(self):
  base=simulate(TASKS,EDGES,300,7,10.,[{'event_id':'R','name':'雨','probability':.4,'delay_hours':2.,'task_ids':['B','A']}])
  shuffled=simulate(list(reversed(TASKS)),list(reversed(EDGES)),300,7,10.,[{'event_id':'R','name':'雨','probability':.4,'delay_hours':2.,'task_ids':['A','B']}])
  self.assertEqual(base['finish_times'],shuffled['finish_times'])
  self.assertEqual(base['events'],shuffled['events'])

class EventSemantics(unittest.TestCase):
 def test_event_occurrence_once_per_sample(self):
  result=simulate(TASKS,EDGES,1000,3,10.,[{'event_id':'R','name':'雨','probability':.3,'delay_hours':2.,'task_ids':['A','B','C']}])
  event=result['events'][0]
  self.assertEqual(event['denominator'],1000)
  self.assertAlmostEqual(event['occurrence_rate'],.3,delta=.06)
  self.assertAlmostEqual(result['event_any_rate'],event['occurrence_rate'])

 def test_hit_adds_fixed_delay_to_each_linked_task(self):
  base=simulate(TASKS,EDGES,200,5,10.)
  hit_all=simulate(TASKS,EDGES,200,5,10.,[{'event_id':'R','name':'雨','probability':1.,'delay_hours':3.,'task_ids':['A','B','C']}])
  # A,B,C form the only path; each sample gains 3h per linked task => +9h.
  for before,after in zip(base['finish_times'],hit_all['finish_times']):
   self.assertAlmostEqual(after-before,9.,places=9)
  self.assertEqual(hit_all['events'][0]['occurrence_count'],200)

 def test_multiple_events_accumulate(self):
  base=simulate(TASKS,EDGES,200,5,10.)
  stacked=simulate(TASKS,EDGES,200,5,10.,[{'event_id':'A1','name':'雨','probability':1.,'delay_hours':2.,'task_ids':['A','B','C']},{'event_id':'B1','name':'管制','probability':1.,'delay_hours':4.,'task_ids':['A','B','C']}])
  for before,after in zip(base['finish_times'],stacked['finish_times']):
   self.assertAlmostEqual(after-before,18.,places=9)
  self.assertEqual([e['occurrence_count'] for e in stacked['events']],[200,200])

 def test_off_path_event_does_not_move_finish(self):
  base=simulate(TASKS,EDGES,200,5,10.)
  # FREE peaks at 2h + 0.5h, always below the A→B→C chain, so project finish is untouched.
  off=simulate(TASKS,EDGES,200,5,10.,[{'event_id':'F','name':'备件','probability':1.,'delay_hours':.5,'task_ids':['FREE']}])
  self.assertEqual(base['finish_times'],off['finish_times'])
  self.assertEqual(off['events'][0]['occurrence_count'],200)

 def test_deadline_and_histogram_use_post_event_finish(self):
  result=simulate(TASKS,EDGES,500,9,10.,[{'event_id':'R','name':'雨','probability':.5,'delay_hours':4.,'task_ids':['A','B','C']}])
  on_time=sum(v<=10.+result['deadline_tolerance_hours'] for v in result['finish_times'])
  self.assertEqual(result['on_time_count'],on_time)
  self.assertAlmostEqual(result['on_time_probability'],on_time/500)
  self.assertEqual(sum(b['count'] for b in result['histogram']),500)

class EventValidation(unittest.TestCase):
 def bad(self,event):
  with self.assertRaises(ValueError):normalize_events([event],TASK_IDS)
 def test_rejections(self):
  good={'event_id':'R','name':'雨','probability':.3,'delay_hours':2.,'task_ids':['A']}
  for change in ({'event_id':'bad id'},{'event_id':''},{'name':''},{'probability':-.1},{'probability':1.1},{'delay_hours':-1},{'delay_hours':float('nan')},{'task_ids':[]},{'task_ids':['A','A']},{'task_ids':['NOPE']}):
   self.bad({**good,**change})
  with self.assertRaises(ValueError):normalize_events([good,good],TASK_IDS)
  with self.assertRaises(ValueError):normalize_events([{**good,'event_id':f'E{i}'} for i in range(21)],TASK_IDS)

 def test_events_sorted_by_id_for_stable_stream(self):
  normalized=normalize_events([{'event_id':'Z','name':'z','probability':.1,'delay_hours':1.,'task_ids':['B','A']},{'event_id':'A','name':'a','probability':.2,'delay_hours':2.,'task_ids':['A']}],TASK_IDS)
  self.assertEqual([e['event_id'] for e in normalized],['A','Z'])
  self.assertEqual(normalized[1]['task_ids'],['A','B'])

class AnalysisContract(unittest.TestCase):
 def test_legacy_snapshot_analyzes_independently(self):
  snapshot={'package':{'tasks':TASKS},'dependencies':[{'predecessor':a,'successor':b} for a,b in EDGES]}
  scenario=type('S',(),{'samples':300,'seed':4,'deadline':10.})
  result=analyze(snapshot,scenario)
  self.assertEqual(result['risk']['events'],[])
  self.assertTrue(result['risk']['independence_assumption'])
  self.assertEqual(result['risk']['event_model'],'independent_durations')
 def test_snapshot_events_frozen_into_result(self):
  events=[{'event_id':'R','name':'雨','probability':.3,'delay_hours':2.,'task_ids':['A','B']}]
  snapshot={'package':{'tasks':TASKS},'dependencies':[{'predecessor':a,'successor':b} for a,b in EDGES],'events':events}
  scenario=type('S',(),{'samples':200,'seed':4,'deadline':10.})
  result=analyze(snapshot,scenario)
  self.assertEqual(result['risk']['events'][0]['event_id'],'R')
  self.assertEqual(result['risk']['event_model'],'shared_stoppage_events')
  self.assertFalse(result['risk']['independence_assumption'])
  self.assertEqual(len(result['assumptions']),6)

class LegacyParity(unittest.TestCase):
 def test_demo_legacy_run_matches_pre_change_implementation(self):
  """The frozen demo baseline must reproduce the pre-change algorithm bit-for-bit."""
  import subprocess
  old_source=subprocess.check_output(['git','-C',BACKEND,'show','HEAD:backend/src/services/pert.py'],text=True)
  from src.services.cpm import cpm,TOLERANCE
  namespace={'cpm':cpm,'TOLERANCE':TOLERANCE}
  exec(compile(old_source,'legacy_pert','exec'),namespace)
  tasks=[{'task_id':f'T{i:02}','name':str(i),'a':float(max(1,i)),'m':float(max(1,i)+1),'b':float(max(1,i)+3)} for i in range(1,9)]
  edges=[('T01','T02'),('T02','T03'),('T03','T04'),('T04','T05'),('T05','T06')]
  legacy=namespace['simulate'](tasks,edges,800,2410,20.)
  current=simulate(tasks,edges,800,2410,20.)
  self.assertEqual(legacy['finish_times'],current['finish_times'])
  self.assertEqual(legacy['task_criticality'],current['task_criticality'])
  self.assertEqual(legacy['on_time_count'],current['on_time_count'])

if __name__=='__main__':unittest.main()
