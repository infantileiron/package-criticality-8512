import uuid,csv,io
from sqlalchemy import select
from fastapi import HTTPException
from src.models import Report,DeliveryReview,ScheduleRun
from src.services.runs import require_completed
from src.utils.serialization import serialize
from src.utils.time import now

def create(db,payload,user):
 require_completed(db,payload.run_id);db.scalar(select(ScheduleRun).where(ScheduleRun.id==payload.run_id).with_for_update())
 review=db.scalar(select(DeliveryReview).where(DeliveryReview.run_id==payload.run_id).order_by(DeliveryReview.version.desc()))
 if not review or review.decision!='accepted':raise HTTPException(409,'最新交付复核须接受后才能归档')
 if db.scalar(select(Report).where(Report.review_id==review.id)):raise HTTPException(409,'此复核版本已归档')
 item=Report(id=str(uuid.uuid4()),review_id=review.id,published_by=user['email'],created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)
def export(db,id):
 report=db.get(Report,id)
 if not report:raise HTTPException(404,'报告不存在')
 run=require_completed(db,report.run_id);result=run.result;review=db.get(DeliveryReview,report.review_id);risk=result['risk'];counts={r['task_id']:r for r in risk['task_criticality']};names={t['task_id']:t['name'] for t in result['tasks']};buf=io.StringIO();writer=csv.DictWriter(buf,['run_id','checksum','review_version','task_id','task_name','duration_hours','es','ef','ls','lf','total_float','baseline_critical','critical_count','denominator','criticality','deadline_hours','deadline_tolerance_hours','on_time_count','on_time_probability','seed']);writer.writeheader()
 for t in result['baseline']['tasks']:writer.writerow({'run_id':run.id,'checksum':result['checksum'],'review_version':review.version,'task_id':t['task_id'],'task_name':names[t['task_id']],'duration_hours':t['duration'],'es':t['es'],'ef':t['ef'],'ls':t['ls'],'lf':t['lf'],'total_float':t['total_float'],'baseline_critical':t['critical'],'critical_count':counts[t['task_id']]['critical_count'],'denominator':risk['samples'],'criticality':counts[t['task_id']]['criticality'],'deadline_hours':risk['deadline'],'deadline_tolerance_hours':risk['deadline_tolerance_hours'],'on_time_count':risk['on_time_count'],'on_time_probability':risk['on_time_probability'],'seed':risk['seed']})
 return chr(0xfeff)+buf.getvalue()
