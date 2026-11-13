import {request} from './client';import type {Scenario} from '../types/domain';
export const list=()=>request<Scenario[]>('/scenarios');
export const create=(data:unknown)=>request<Scenario>('/scenarios',data);
