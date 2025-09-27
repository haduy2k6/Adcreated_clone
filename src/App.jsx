import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import MyBanner from './component/Banner/MyBanner.jsx'
import { SignPage} from './component/login/Login.jsx';

function App() {
  const [count, setCount] = useState(0)

  return (
   <BrowserRouter>
      <Routes>
        <Route path="/" element={<MyBanner />} /> {/* Sử dụng MyBanner làm trang mặc định */}
        <Route path="/login" element={<SignPage/>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
