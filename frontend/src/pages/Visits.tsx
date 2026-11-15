import React, { useEffect, useState } from 'react'
import { api } from '../api/client'
export default function Visits(){
  const token=localStorage.getItem('token')||''
  const [visits,setVisits]=useState<any[]>([])
  const [name,setName]=useState('John Doe')
  const load=async()=>{ const v=await api.listVisits(token); setVisits(v)}
  useEffect(()=>{load()},[])
  const create=async()=>{ await api.createVisit(token,{patient_name:name}); load()}
  if(!token) location.href='/login'
  return <div className="p-6 space-y-4">
    <h1 className="text-2xl font-bold">ClinicOps — Visits</h1>
    <div className="flex gap-2"><input className="input w-64" value={name} onChange={e=>setName(e.target.value)} /><button className="btn" onClick={create}>New Visit</button><button className="btn bg-gray-600" onClick={()=>{localStorage.clear(); location.href='/login'}}>Logout</button></div>
    <table className="w-full bg-white rounded shadow"><thead><tr><th className="th">ID</th><th className="th">Patient</th><th className="th">Status</th><th className="th">Deadline</th><th className="th">Action</th></tr></thead><tbody>{visits.map(v=><tr key={v.id} className="border-t"><td className="td">{v.id}</td><td className="td">{v.patient_name}</td><td className="td"><span className="px-2 py-1 rounded bg-blue-100">{v.status}</span></td><td className="td">{v.deadline_at ? new Date(v.deadline_at).toLocaleString() : '-'}</td><td className="td"><a className="text-blue-600 underline" href={`/visits/${v.id}`}>Open</a></td></tr>)}</tbody></table>
    <p className="text-xs text-gray-500">Multimodal: open a visit to upload CSV+JPG+WAV/PDF, compute scores, trigger AI</p>
  </div>
}
