import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Map from './components/Map'
import RiverDetail from './components/RiverDetail'
import { useRivers } from './hooks/useRivers'

export default function App() {
  const { rivers, loading, error, lastUpdated, refetch } = useRivers()
  const [selectedRiverId, setSelectedRiverId] = useState(null)
  const [showDetail, setShowDetail] = useState(false)

  const handleSelectRiver = (riverId) => {
    setSelectedRiverId(riverId)
    setShowDetail(true)
  }

  const handleBackFromDetail = () => {
    setShowDetail(false)
  }

  const getMinutesAgo = (date) => {
    if (!date) return null
    const now = new Date()
    const diff = now - date
    const minutes = Math.floor(diff / 60000)
    if (minutes < 1) return 'just now'
    if (minutes === 1) return '1 minute ago'
    if (minutes < 60) return `${minutes} minutes ago`
    const hours = Math.floor(minutes / 60)
    if (hours === 1) return '1 hour ago'
    return `${hours} hours ago`
  }

  return (
    <div className="w-full h-screen bg-bg-light flex flex-col md:flex-row overflow-hidden">
      {/* Header for mobile */}
      <div className="md:hidden p-4 bg-white border-b border-gray-200 flex items-center justify-between">
        <h1 className="text-xl font-bold text-text-primary flex items-center gap-2">
          <span>🎣</span> NorCal Flows
        </h1>
        <button
          onClick={refetch}
          className="px-3 py-1 bg-blue-600 text-white text-xs font-medium rounded-md hover:bg-blue-700 transition"
        >
          Refresh
        </button>
      </div>

      {/* Sidebar */}
      <div className="hidden md:flex md:flex-col md:h-full md:w-96">
        <Sidebar
          rivers={rivers}
          loading={loading}
          selectedRiverId={selectedRiverId}
          onSelectRiver={handleSelectRiver}
        />
      </div>

      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Status bar */}
        <div className="px-4 py-3 bg-white border-b border-gray-200 flex items-center justify-between text-xs text-text-muted">
          <div className="flex items-center gap-2">
            {error && (
              <span className="text-status-red font-medium">
                Error: {error}
              </span>
            )}
            {!error && lastUpdated && (
              <span>Updated {getMinutesAgo(lastUpdated)}</span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <span>{rivers.length} rivers</span>
            <button
              onClick={refetch}
              disabled={loading}
              className="px-2 py-1 hover:bg-gray-100 rounded transition disabled:opacity-50"
            >
              {loading ? '⟳' : '↻'}
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex">
          {/* Map */}
          <div className="flex-1 relative">
            {loading && rivers.length === 0 ? (
              <div className="w-full h-full flex items-center justify-center bg-gray-50">
                <p className="text-text-muted">Loading river data...</p>
              </div>
            ) : (
              <Map
                rivers={rivers}
                selectedRiverId={selectedRiverId}
                onSelectRiver={handleSelectRiver}
              />
            )}

            {/* Mobile sidebar toggle (visible only on small screens when detail is open) */}
            {showDetail && (
              <button
                onClick={handleBackFromDetail}
                className="md:hidden absolute bottom-4 left-4 px-4 py-2 bg-white text-text-primary font-medium rounded-lg shadow-lg"
              >
                ← Back to Map
              </button>
            )}
          </div>

          {/* Detail panel - shown on desktop or when selected on mobile */}
          {selectedRiverId && (
            <div className="hidden md:flex md:w-96 md:border-l md:border-gray-200 md:overflow-hidden">
              <RiverDetail
                riverId={selectedRiverId}
                onBack={handleBackFromDetail}
              />
            </div>
          )}
        </div>

        {/* Mobile detail sheet */}
        {showDetail && selectedRiverId && (
          <div className="md:hidden absolute inset-0 z-50 flex flex-col">
            {/* Backdrop */}
            <div
              className="flex-1 bg-black bg-opacity-50"
              onClick={handleBackFromDetail}
            />
            {/* Detail panel */}
            <div className="bg-white rounded-t-xl shadow-lg overflow-hidden flex flex-col max-h-[90vh]">
              <div className="p-4 border-b border-gray-200">
                <button
                  onClick={handleBackFromDetail}
                  className="text-blue-600 font-medium text-sm"
                >
                  ← Back
                </button>
              </div>
              <div className="flex-1 overflow-y-auto">
                <div className="p-4">
                  <RiverDetail
                    riverId={selectedRiverId}
                    onBack={handleBackFromDetail}
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
