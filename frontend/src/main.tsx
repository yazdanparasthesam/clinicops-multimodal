import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Visits from './pages/Visits'
import VisitDetail from './pages/VisitDetail'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <BrowserRouter>
    <Routes>
      <Route path="/login" element={<Login/>} />
      <Route path="/visits" element={<Visits/>} />
      <Route path="/visits/:id" element={<VisitDetail/>} />
      <Route path="/" element={<Navigate to="/visits" replace/>} />
    </Routes>
  </BrowserRouter>
)
