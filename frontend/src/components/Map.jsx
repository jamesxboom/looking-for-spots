import { useEffect, useRef } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'

// Fix for default marker icons in react-leaflet
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

function MapContent({ rivers, selectedRiverId, onSelectRiver }) {
  const map = useMap()
  const markersRef = useRef({})

  const statusColors = {
    green: '#22c55e',
    yellow: '#eab308',
    red: '#ef4444',
  }

  // Fit bounds to all rivers on mount
  useEffect(() => {
    if (rivers.length === 0) return

    const bounds = L.latLngBounds(
      rivers.map((r) => [r.latitude, r.longitude])
    )
    map.fitBounds(bounds, { padding: [100, 100] })
  }, [rivers, map])

  // Animate selected marker
  useEffect(() => {
    Object.values(markersRef.current).forEach((marker) => {
      if (marker._container) {
        marker._container.classList.remove('pulse-marker')
      }
    })

    if (selectedRiverId && markersRef.current[selectedRiverId]) {
      const selectedMarker = markersRef.current[selectedRiverId]
      if (selectedMarker._container) {
        selectedMarker._container.classList.add('pulse-marker')
      }
      map.flyTo(selectedMarker.getLatLng(), 9, { duration: 1 })
    }
  }, [selectedRiverId, map])

  return (
    <>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap contributors'
        maxZoom={18}
      />

      {rivers.map((river) => (
        <CircleMarker
          key={river.id}
          center={[river.latitude, river.longitude]}
          radius={12}
          fillColor={statusColors[river.status] || statusColors.yellow}
          fillOpacity={0.8}
          color="white"
          weight={2}
          opacity={1}
          eventHandlers={{
            click: () => onSelectRiver(river.id),
          }}
          ref={(marker) => {
            if (marker) markersRef.current[river.id] = marker
          }}
        >
          <Popup offset={[0, -10]}>
            <div className="p-2 min-w-max">
              <h4 className="font-semibold text-sm mb-1">{river.name}</h4>
              <div className="text-xs space-y-1">
                <p>
                  <span className="font-medium">{river.currentCfs?.toLocaleString() || '—'}</span>{' '}
                  cfs
                </p>
                {river.waterTempF && (
                  <p>
                    <span className="font-medium">{river.waterTempF}</span>°F
                  </p>
                )}
                <p className="text-gray-600">
                  Tap for details →
                </p>
              </div>
            </div>
          </Popup>
        </CircleMarker>
      ))}
    </>
  )
}

export default function Map({ rivers, selectedRiverId, onSelectRiver }) {
  return (
    <MapContainer
      center={[39.8, -121.0]}
      zoom={7}
      scrollWheelZoom={true}
      style={{ height: '100%', width: '100%' }}
      className="rounded-lg"
    >
      <MapContent
        rivers={rivers}
        selectedRiverId={selectedRiverId}
        onSelectRiver={onSelectRiver}
      />
    </MapContainer>
  )
}
