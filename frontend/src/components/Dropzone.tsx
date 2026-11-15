import React, { useState } from 'react'
export default function Dropzone({onUpload}:{onUpload:(f:File)=>Promise<void>}) {
  const [drag,setDrag]=useState(false)
  return (
    <div onDragOver={e=>{e.preventDefault(); setDrag(true)}} onDragLeave={()=>setDrag(false)} onDrop={async e=>{e.preventDefault(); setDrag(false); const f=e.dataTransfer.files[0]; if(f) await onUpload(f)}} className={`border-2 border-dashed rounded p-6 text-center ${drag?'bg-blue-50':''}`}>
      <p>Drag CSV / JPG / WAV / PDF here or <label className="text-blue-600 underline cursor-pointer">browse<input type="file" hidden onChange={async e=>{const f=e.target.files?.[0]; if(f) await onUpload(f)}} /></label></p>
      <p className="text-xs text-gray-500">MIME: image/jpeg,png, audio/webm,wav,mp3, application/pdf, text/csv ≤10MB</p>
    </div>
  )
}
