import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
        <h1>🎬 OTT Discovery Platform (Starter)</h1>
        <p>Welcome to the 10-day hackathon project starter.</p>
        <hr />
        <Routes>
          <Route path="/" element={<div>Home Page (Mock Data Here)</div>} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}
