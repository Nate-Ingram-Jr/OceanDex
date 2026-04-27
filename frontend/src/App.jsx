import { Routes, Route } from 'react-router-dom'
import NavBar from './components/NavBar'
import Explore from './pages/Home'
import SpeciesDetailPage from './pages/SpeciesDetail'
import ProtectedList from './pages/ProtectedList'
import IDScanner from './pages/IDScanner'
import OceanMap from './pages/OceanMap'
import Login from './pages/Login'
import SubmitCreature from './pages/SubmitCreature'
import AdminDashboard from './pages/AdminDashboard'
import { AuthProvider } from './context/AuthContext'

export default function App() {
  return (
    <AuthProvider>
      <div className="app">
        <NavBar />
        <div className="page">
          <Routes>
            <Route path="/" element={<Explore />} />
            <Route path="/species/:id" element={<SpeciesDetailPage />} />
            <Route path="/protected" element={<ProtectedList />} />
            <Route path="/id-scanner" element={<IDScanner />} />
            <Route path="/ocean-map" element={<OceanMap />} />
            <Route path="/login" element={<Login />} />
            <Route path="/submit" element={<SubmitCreature />} />
            <Route path="/admin" element={<AdminDashboard />} />
          </Routes>
        </div>
      </div>
    </AuthProvider>
  )
}
