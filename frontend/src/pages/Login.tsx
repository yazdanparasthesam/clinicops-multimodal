import React, { useState } from 'react'
import { api } from '../api/client'
export default function Login(){
  const [email,setEmail]=useState('nurse@example.com')
  const [password,setPassword]=useState('password123')
  const [msg,setMsg]=useState('')
  const login=async()=>{
    try { const r=await api.login(email,password); localStorage.setItem('token',r.access_token); localStorage.setItem('email',email); location.href='/visits'; }
    catch(e:any){ setMsg(e.message) }
  }
  const register=async(role:string)=>{
    try { await api.register(email,password,role); setMsg(`Registered ${role} — now login`) } catch(e:any){ setMsg(e.message) }
  }
  return <div className="min-h-screen flex items-center justify-center bg-gray-50"><div className="card w-96 space-y-4">
    <h1 className="text-xl font-bold">ClinicOps — Login</h1>
    <p className="text-xs text-gray-500">Demo: nurse@example.com / doctor@example.com / pharmacist@example.com — password123 (register first via button)</p>
    <input className="input" value={email} onChange={e=>setEmail(e.target.value)} placeholder="email@example.com" />
    <input className="input" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
    <button className="btn w-full" onClick={login}>Login</button>
    <div className="flex gap-2"><button className="btn flex-1 bg-gray-600" onClick={()=>register('nurse')}>Register nurse</button><button className="btn flex-1 bg-gray-600" onClick={()=>register('doctor')}>Register doctor</button><button className="btn flex-1 bg-gray-700" onClick={()=>register('pharmacist')}>Register pharmacist</button></div>
    {msg && <p className="text-sm text-red-600">{msg}</p>}
  </div></div>
}
