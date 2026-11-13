import {request} from './client';import type {Dependency} from '../types/domain';
export const list=()=>request<Dependency[]>('/dependencies');
export const create=(data:unknown)=>request<Dependency>('/dependencies',data);
