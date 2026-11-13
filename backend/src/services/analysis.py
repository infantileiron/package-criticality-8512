import hashlib,json
from src.services.cpm import cpm
from src.services.pert import simulate

def analyze(snapshot,scenario):
 tasks=snapshot['package']['tasks'];edges=[[e['predecessor'],e['successor']] for e in snapshot['dependencies']]
 baseline=cpm({t['task_id']:t['m'] for t in tasks},edges);risk=simulate(tasks,edges,scenario.samples,scenario.seed,scenario.deadline)
 data={'snapshot':snapshot,'samples':scenario.samples,'seed':scenario.seed,'deadline':scenario.deadline}
 return {'baseline':baseline,'risk':risk,'tasks':tasks,'edges':edges,'checksum':hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'assumptions':['单位为小时；依赖仅零等待finish-start，多源多汇及孤立任务通过虚拟源/汇的共同边界统一。','CPM使用最可能m工期。每次模拟重新计算依赖最大完工与总时差；所有LF以该次实际项目完工为基准，不用外部deadline。','Beta-PERT lambda=4；alpha=1+4(m-a)/(b-a)，beta=1+4(b-m)/(b-a)，a=m=b为点质量，不调用Beta。','任务工期相互独立；固定seed与ID顺序复现。关键度为总时差<=1e-8小时的次数/全部样本数；不把基线关键集合套到每次模拟。','达标比较为每次项目完工<=deadline+1e-8小时，仅消除浮点边界误差；有限样本比例不是工期保证，也不是资源约束排程。','未模拟天气共因、共享人员设备、日历与资源竞争；模型输出仅供模拟工务计划人工复核。']}
