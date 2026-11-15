import React, { useState, useRef } from 'react'
export default function AudioRecorder({onBlob}:{onBlob:(b:Blob)=>void}) {
  const [rec,setRec]=useState(false)
  const mr=useRef<MediaRecorder|null>(null)
  const start=async()=>{
    const stream=await navigator.mediaDevices.getUserMedia({audio:true})
    const r=new MediaRecorder(stream)
    const chunks:BlobPart[]=[]
    r.ondataavailable=e=>chunks.push(e.data)
    r.onstop=()=>onBlob(new Blob(chunks,{type:'audio/webm'}))
    r.start(); mr.current=r; setRec(true)
  }
  const stop=()=>{mr.current?.stop(); setRec(false)}
  return <div className="flex gap-2"><button onClick={rec?stop:start} className="btn">{rec?'Stop':'Record memo'}</button><span className="text-sm text-gray-500">{rec?'Recording...':''}</span></div>
}
