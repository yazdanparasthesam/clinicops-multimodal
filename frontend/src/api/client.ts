const BASE = import.meta.env.VITE_API_URL || ''
const apiBase = BASE ? `${BASE}/api` : '/api'

function headers(token?: string) {
  const h: Record<string,string> = { 'Content-Type': 'application/json' }
  if (token) h['Authorization'] = `Bearer ${token}`
  const tid = (window as any).__traceId
  if (tid) h['X-Trace-Id'] = tid
  return h
}

export const api = {
  login: async (email:string,password:string) => {
    const r = await fetch(`${apiBase}/auth/login`, {method:'POST', headers: headers(), body: JSON.stringify({email,password})})
    if (!r.ok) throw new Error(await r.text())
    return r.json()
  },
  register: async (email:string,password:string,role:string) => {
    const r= await fetch(`${apiBase}/auth/register`,{method:'POST', headers: headers(), body: JSON.stringify({email,password,role})})
    if (!r.ok) throw new Error(await r.text())
    return r.json()
  },
  listVisits: async (token:string) => (await fetch(`${apiBase}/visits`,{headers: headers(token)})).json(),
  createVisit: async (token:string, data:any) => {
    const r=await fetch(`${apiBase}/visits`,{method:'POST', headers: headers(token), body: JSON.stringify(data)})
    if (!r.ok) throw new Error(await r.text())
    return r.json()
  },
  getVisit: async (token:string, id:string)=> (await fetch(`${apiBase}/visits/${id}`,{headers: headers(token)})).json(),
  patchVisit: async (token:string, id:string, data:any) => {
    const r=await fetch(`${apiBase}/visits/${id}`,{method:'PATCH', headers: headers(token), body: JSON.stringify(data)})
    if (!r.ok) throw new Error(await r.text())
    return r.json()
  },
  getValidations: async (t:string,id:string)=>(await fetch(`${apiBase}/visits/${id}/validations`,{headers: headers(t)})).json(),
  getAttachments: async (t:string,id:string)=>(await fetch(`${apiBase}/visits/${id}/attachments`,{headers: headers(t)})).json(),
  uploadAttachment: async (token:string, id:string, file:File) => {
    const fd=new FormData(); fd.append('file',file)
    const r=await fetch(`${apiBase}/visits/${id}/attachments`,{method:'POST', headers:{'Authorization':`Bearer ${token}`}, body: fd})
    if (!r.ok) throw new Error(await r.text())
    return r.json()
  },
  visionDraft: async(t:string,id:string)=>(await fetch(`${apiBase}/visits/${id}/ai/vision-draft`,{method:'POST', headers: headers(t), body: JSON.stringify({})})).json(),
  transcribe: async(t:string,id:string, transcript:string, conf:number)=>(await fetch(`${apiBase}/visits/${id}/ai/transcribe`,{method:'POST', headers: headers(t), body: JSON.stringify({transcript, confidence:conf})})).json(),
  notesDraft: async(t:string,id:string)=>(await fetch(`${apiBase}/visits/${id}/ai/notes-draft`,{method:'POST', headers: headers(t), body: JSON.stringify({})})).json(),
  chat: async(t:string,id:string, query:string)=>(await fetch(`${apiBase}/visits/${id}/ai/chat`,{method:'POST', headers: headers(t), body: JSON.stringify({query})})).json(),
  workflow: async(t:string,id:string,action:string, note?:string)=>{
    const r=await fetch(`${apiBase}/visits/${id}/workflow/${action}`,{method:'POST', headers: headers(t), body: JSON.stringify({note})})
    if (!r.ok) throw new Error(await r.text())
    return r.json()
  },
  checklist: async(t:string,id:string)=>(await fetch(`${apiBase}/visits/${id}/export/checklist`,{headers: headers(t)})).json(),
}
export const download = async (token:string, url:string) => {
  const r=await fetch(url,{headers: headers(token)})
  if (!r.ok) throw new Error(await r.text())
  return r.blob()
}
