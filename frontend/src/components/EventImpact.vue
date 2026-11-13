<script setup lang="ts">
import {computed} from 'vue';
import type {Risk,Task} from '../types/domain';
import {pct} from '../utils/format';
const props=defineProps<{risk:Risk;tasks:Task[]}>();
const name=(id:string)=>props.tasks.find(t=>t.task_id===id)?.name;
const events=computed(()=>props.risk.events??[]);
const anyCount=computed(()=>props.risk.event_any_count??0);
const anyRate=computed(()=>props.risk.event_any_rate??0);
</script>
<template>
 <div class="event-impact">
  <p class="muted">每个样本对每个事件只判定一次，命中后固定延误叠加到全部关联任务；多个事件可在同一样本命中并累加。下方发生次数为命中样本数，分母为全部 {{risk.samples}} 次抽样。</p>
  <div class="table-scroll">
   <table>
    <thead><tr><th>事件</th><th>发生概率</th><th>固定延误 / h</th><th>关联任务</th><th>发生次数</th><th>发生率</th></tr></thead>
    <tbody>
     <tr v-for="e in events" :key="e.event_id">
      <td><b>{{e.event_id}}</b> {{e.name}}</td>
      <td>{{e.probability}}</td>
      <td>{{e.delay_hours}}</td>
      <td class="event-task-list"><span v-for="id in e.task_ids" :key="id">{{id}} {{name(id)}}</span></td>
      <td>{{e.occurrence_count}} / {{e.denominator}}</td>
      <td>{{pct(e.occurrence_rate)}}</td>
     </tr>
    </tbody>
   </table>
  </div>
  <div class="event-any">
   <span>至少命中一个事件的样本</span>
   <b>{{anyCount}} / {{risk.samples}}</b>
   <strong>{{pct(anyRate)}}</strong>
   <small>达标率 {{pct(risk.on_time_probability)}} 已按叠加事件后的完工时间计算；与独立工期口径不可直接比较。</small>
  </div>
 </div>
</template>
