import { useState, useEffect } from 'react'
import Map from './components/Map'
import Sidebar from './components/Sidebar'
import type { Route } from './types'
import './App.css'

function App() {
  const [routes, setRoutes] = useState<Route[]>([])
  const [selectedRoute, setSelectedRoute] = useState<Route | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/routes')
      .then(res => res.json())
      .then(data => {
        setRoutes(data)
        setLoading(false)
      })
      .catch(err => {
        console.error("Error fetching routes:", err)
        setLoading(false)
      })
  }, [])

  return (
    <div className="app-container">
      <div className="sidebar-container">
        <Sidebar selectedRoute={selectedRoute} totalRoutes={routes.length} />
      </div>
      <div className="map-container">
        {loading ? (
          <div className="loading">Loading routes...</div>
        ) : (
          <Map
            routes={routes}
            selectedRoute={selectedRoute}
            onSelectRoute={setSelectedRoute}
          />
        )}
      </div>
    </div>
  )
}

export default App
