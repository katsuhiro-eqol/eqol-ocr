import { Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import DemoApp from './pages/DemoApp'

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/app" element={<DemoApp />} />
    </Routes>
  )
}

export default App
