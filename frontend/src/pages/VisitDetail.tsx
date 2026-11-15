import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../api/client'
import Dropzone from '../components/Dropzone'
import AudioRecorder from '../components/AudioRecorder'

export default function VisitDetail(){
  const {id}=useParams()
  const token=localStorage.getItem('token')||''
  const [visit,setVisit]=useState<any>(null)
  const [validations,setValidations]=useState<any[]>([])
  const [attachments,setAttachments]=useState<any[]>([])
  const [weight,setWeight]=useState('70'); const [height,setHeight]=useState('175'); const [sys,setSys]=useState('120'); const [dia,setDia]=useState('80')
  const load=async()=>{
    const v=await api.getVisit(token,id!); setVisit(v)
    const vs=await api.getValidations(token,id!); setValidations(vs)
    const atts=await api.getAttachments(token,id!); setAttachments(atts)
  }
  useEffect(()=>{load()},[])
  const patchVitals=async()=>{
    await api.patchVisit(token,id!,{weight_kg: parseFloat(weight), height_cm: parseFloat(height), systolic: parseFloat(sys), diastolic: parseFloat(dia), age:40, creatinine:1.0, sex:'male', dose_mg:100})
    load()
  }
  const onUpload=async(f:File)=>{ await api.uploadAttachment(token,id!,f); load()}
  const onRecord=async(blob:Blob)=>{ const f=new File([blob],'memo.webm',{type:'audio/webm'}); await onUpload(f)}
  if(!visit) return <div className="p-6">Loading...</div>
  return <div className="p-6 space-y-4">
    <a href="/visits" className="text-blue-600">← Back</a>
    <h1 className="text-xl font-bold">Visit {visit.id} — {visit.patient_name} [{visit.status}]</h1>
    <div className="grid grid-cols-3 gap-4">
      <div className="card space-y-2"><h3 className="font-semibold">Vitals → Scores</h3>
        <div className="grid grid-cols-2 gap-2"><input className="input" value={weight} onChange={e=>setWeight(e.target.value)} placeholder="weight_kg" /><input className="input" value={height} onChange={e=>setHeight(e.target.value)} placeholder="height_cm" /><input className="input" value={sys} onChange={e=>setSys(e.target.value)} placeholder="systolic" /><input className="input" value={dia} onChange={e=>setDia(e.target.value)} placeholder="diastolic" /></div>
        <button className="btn w-full" onClick={patchVitals}>Recompute Scores</button>
        <pre className="text-xs bg-gray-50 p-2 rounded">{JSON.stringify(visit.scores,null,2)}</pre>
      </div>
      <div className="card"><h3 className="font-semibold">Validations R001-R008</h3>{validations.map(v=><div key={v.id} className={`p-2 rounded mb-1 ${v.severity==='error'?'bg-red-50':'bg-amber-50'}`}><b>{v.rule_id}</b> [{v.severity}] {v.message}</div>)}{validations.length===0 && <p className="text-sm text-green-600">All checks passed</p>}</div>
      <div className="card space-y-2"><h3 className="font-semibold">Workflow</h3>
        <div className="flex flex-wrap gap-2">
          {['submit','start_review','approve','dispense','request_changes','reject','reopen'].map(a=><button key={a} className="btn text-xs" onClick={async()=>{try{await api.workflow(token,id!,a); load()}catch(e:any){alert(e.message)}} }>{a}</button>)}
        </div>
        <p className="text-xs">72h deadline: {visit.deadline_at}</p>
        <div className="flex gap-2"><a className="text-blue-600 text-xs underline" href={`/api/visits/${id}/export/pdf`} target="_blank">PDF</a><a className="text-blue-600 text-xs underline" href={`/api/visits/${id}/export/xlsx`} target="_blank">XLSX</a></div>
      </div>
    </div>
    <div className="grid grid-cols-2 gap-4">
      <div className="card space-y-2"><h3 className="font-semibold">Multimodal Attachments</h3><Dropzone onUpload={onUpload} /><AudioRecorder onBlob={onRecord} /><ul className="text-sm">{attachments.map(a=><li key={a.id}>{a.kind} — {a.filename} ({a.mime}) {a.size}B SHA:{a.sha256.slice(0,8)}</li>)}</ul></div>
      <div className="card space-y-2"><h3 className="font-semibold">AI Assist (Vision / Transcribe / Notes / Chat)</h3>
        <button className="btn w-full" onClick={async()=>{const r=await api.visionDraft(token,id!); alert(r.content)}}>Vision Finding Draft (self-criticism)</button>
        <button className="btn w-full" onClick={async()=>{const r=await api.transcribe(token,id!,'45yo male chest pain, Wells 2, plan ECG',0.92); alert(r.content)}}>Transcribe Memo → SOAP</button>
        <button className="btn w-full bg-purple-600" onClick={async()=>{const r=await api.notesDraft(token,id!); alert(r.content)}}>Discharge Notes Draft</button>
        <button className="btn w-full bg-gray-700" onClick={async()=>{const r=await api.chat(token,id!,'Summarize scores and validations'); alert(r.content)}}>ReAct Chat</button>
        <div className="text-xs bg-gray-50 p-2 rounded">Vision: {visit.vision_finding || '—'} <br/>Transcript: {visit.transcript || '—'}</div>
      </div>
    </div>
  </div>
}
