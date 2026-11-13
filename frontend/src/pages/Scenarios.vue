<script setup lang="ts">
import {ref,computed,watch} from 'vue';
import type {Workspace} from '../stores/workspace';
import {create} from '../api/scenarios';
import * as runs from '../api/runs';
import {useAction} from '../hooks/useAction';
import Heading from '../components/common/Heading.vue';
import Notice from '../components/common/Notice.vue';
import Empty from '../components/common/Empty.vue';
import ScenarioStrip from '../components/ScenarioStrip.vue';
const props=defineProps<{data:Workspace;canWrite:boolean;refresh:()=>Promise<void>}>();
const emit=defineEmits<{open:[string]}>();
const name=ref('检修工作包·新风险情景'),pkg=ref('demo-package'),deadline=ref(32),samples=ref(1500),seed=ref(2410);
type Draft={event_id:string;name:string;probability:number|string;delay_hours:number|string;task_ids:string[]};
const drafts=ref<Draft[]>([]);
const pkgTasks=computed(()=>props.data.packages.find(p=>p.id===pkg.value)?.tasks??[]);
const{busy,error,notice,act}=useAction();
function addEvent(){drafts.value.push({event_id:'W'+(drafts.value.length+1),name:'',probability:0.3,delay_hours:4,task_ids:[]})}
function removeEvent(index:number){drafts.value.splice(index,1)}
function eventPayload(){return drafts.value.map(d=>({event_id:d.event_id.trim(),name:d.name.trim(),probability:Number(d.probability),delay_hours:Number(d.delay_hours),task_ids:d.task_ids}))}
async function freeze(){
 const events=eventPayload();
 const bad=drafts.value.findIndex((d,i)=>!events[i].event_id||!events[i].name||!Number.isFinite(events[i].probability)||events[i].probability<0||events[i].probability>1||!Number.isFinite(events[i].delay_hours)||events[i].delay_hours<0||!events[i].task_ids.length);
 if(bad>=0){throw new Error(`停工事件 ${bad+1} 须填写ID、名称、0至1概率、非负延误并至少关联一个任务`)}
 await create({name:name.value,package_id:pkg.value,deadline:deadline.value,samples:samples.value,seed:seed.value,events});await props.refresh()
}
watch(pkg,()=>{const ids=new Set(pkgTasks.value.map(t=>t.task_id));drafts.value.forEach(d=>{d.task_ids=d.task_ids.filter(id=>ids.has(id))})});
</script>
<template>
 <Heading index="04 / IMMUTABLE SCENARIOS" title="截止期只问概率，不改写时差。" detail="每次保存新增工作包情景版本，冻结任务、FS边、三点范围和停工事件。CPM/每次模拟LF均基于项目实际完工。"/>
 <section v-if="canWrite" class="form-section">
  <form class="form-grid" @submit.prevent="act(freeze,'风险情景快照已冻结，可提交后台推演')">
   <label>情景名称<input aria-label="情景名称" v-model="name" required/></label>
   <label>情景工作包<select aria-label="情景工作包" v-model="pkg"><option v-for="p in data.packages" :key="p.id" :value="p.id">{{p.name}}</option></select></label>
   <label>截止期 / 小时<input aria-label="截止期小时" type="number" min="0" step="any" v-model.number="deadline"/></label>
   <label>模拟样本数<input aria-label="模拟样本数" type="number" min="100" max="5000" step="1" v-model.number="samples"/></label>
   <label>固定seed<input aria-label="固定seed" type="number" min="0" max="2147483647" step="1" v-model.number="seed"/></label>
   <div class="actions"><button type="button" @click="addEvent">+ 添加停工事件</button><small v-if="!drafts.length">未配置事件即保持原独立工期抽样。</small></div>
   <div v-if="drafts.length" class="event-editor">
    <p class="muted">同场降雨等停工事件在同一个样本中只判定一次；命中后固定延误叠加到全部关联任务，多个事件可同时命中并累加。事件按ID排序判定。</p>
    <fieldset v-for="(d,i) in drafts" :key="i" class="event-draft">
     <legend>事件 {{i+1}}</legend>
     <label>事件ID<input :aria-label="'事件ID '+(i+1)" v-model="d.event_id" required maxlength="24" placeholder="RAIN"/></label>
     <label>事件名称<input :aria-label="'事件名称 '+(i+1)" v-model="d.name" required maxlength="80" placeholder="降雨停工"/></label>
     <label>发生概率 0–1<input :aria-label="'发生概率 '+(i+1)" type="number" min="0" max="1" step="any" v-model.number="d.probability"/></label>
     <label>固定延误 / 小时<input :aria-label="'固定延误 '+(i+1)" type="number" min="0" step="any" v-model.number="d.delay_hours"/></label>
     <label class="event-tasks">关联任务<select :aria-label="'关联任务 '+(i+1)" multiple size="6" v-model="d.task_ids"><option v-for="t in pkgTasks" :key="t.task_id" :value="t.task_id">{{t.task_id}} {{t.name}}</option></select><small>按住 Ctrl/Cmd 多选；仅限本工作包任务。</small></label>
     <button type="button" @click="removeEvent(i)">移除该事件</button>
    </fieldset>
   </div>
   <button class="primary" :disabled="busy">冻结风险情景</button>
  </form>
  <Notice :error="error" :notice="notice"/>
 </section>
 <Empty v-if="!data.scenarios.length">先导入工作包并建立无环FS依赖，再锁定截止期、样本数、seed与停工事件。</Empty>
 <article v-for="s in data.scenarios" :key="s.id" class="scenario-row">
  <div>
   <p class="eyebrow">SNAPSHOT v{{s.version}} / {{s.snapshot.package.tasks.length}} TASKS / {{s.snapshot.dependencies.length}} EDGES / {{(s.snapshot.events||[]).length}} EVENTS</p>
   <h2>{{s.name}}</h2>
   <p>{{s.snapshot.package.source}}</p>
   <div v-if="(s.snapshot.events||[]).length" class="event-snapshot">
    <p v-for="e in s.snapshot.events" :key="e.event_id"><b>{{e.event_id}}</b> {{e.name}} · 概率 {{e.probability}} · 固定延误 {{e.delay_hours}}h · {{e.task_ids.length}}任务</p>
   </div>
   <ScenarioStrip :scenario="s"/>
  </div>
  <div>
   <button v-if="canWrite" :disabled="busy" @click="act(async()=>{const r=await runs.create({scenario_id:s.id});await refresh();emit('open',r.id)},'风险任务已提交Redis')">运行CPM与风险 →</button>
   <small>{{data.runs.filter(r=>r.scenario_id===s.id).length}}次独立运行</small>
  </div>
 </article>
 <p class="footnote">Beta-PERT λ=4。a=m=b为常数，其余alpha=1+4(m-a)/(b-a)，beta=1+4(b-m)/(b-a)。固定seed与ID顺序复现；无事件时保持独立工期抽样，有事件时叠加共因停工延误。</p>
</template>
