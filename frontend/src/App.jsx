import { Routes, Route } from 'react-router-dom'
import NavBar from './components/NavBar'
import Explore from './pages/Home'
import SpeciesDetailPage from './pages/SpeciesDetail'
import ProtectedList from './pages/ProtectedList'
import IDScanner from './pages/IDScanner'
import OceanMap from './pages/OceanMap'

export default function App() {
  return (
    <div className="app">
      <NavBar />
      <div className="page">
        <Routes>
          <Route path="/" element={<Explore />} />
          <Route path="/species/:id" element={<SpeciesDetailPage />} />
          <Route path="/protected" element={<ProtectedList />} />
          <Route path="/id-scanner" element={<IDScanner />} />
          <Route path="/ocean-map" element={<OceanMap />} />
        </Routes>
      </div>
    </div>
  )
}
