import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import MyBanner from './component/MyBanner'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <MyBanner/>
    </>
  )
}

export default App
