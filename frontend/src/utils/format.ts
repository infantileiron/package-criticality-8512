export const num=(v:number,d=2)=>Number.isFinite(v)?v.toFixed(d):'不可估计';
export const pct=(v:number)=>num(v*100,1)+'%';
export const short=(s:string)=>s.slice(0,12);
