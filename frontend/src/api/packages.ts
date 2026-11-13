import {request} from './client';import type {Package} from '../types/domain';
export const list=()=>request<Package[]>('/packages');
export const create=(data:unknown)=>request<Package>('/packages',data);
