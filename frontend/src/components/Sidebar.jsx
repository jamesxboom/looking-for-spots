import { useState } from 'react'
import RiverCard from './RiverCard'

export default function Sidebar({ rivers, loading, selectedRiverId, onSelectRiver }) {
  const [sortBy, setSortBy] = useState('status') // 'status', 'name', 'region'

  const sortedRivers = [...rivers].sort((a, b) => {
    if (sortBy === 'status') {
      const statusOrder = { green: 0, yellow: 1, red: 2 }
      return (statusOrder[a.status] || 2) - (statusOrder[b.status] || 2)
    } else if (sortBy === 'name') {
      return a.name.localeCompare(b.name)
    } else if (sortBy === 'region') {
      return (a.region || '').localeCompare(b.region || '')
    }
    return 0
  })

  return (
    <div className="w-full md:w-96 h-full flex flex-col bg-white border-r border-gray-200">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 flex-shrink-0">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2">
            <span className="text-2xl">🎣</span>
            NorCal Flows
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <label htmlFor="sort" className="text-xs font-medium text-text-muted">
            Sort by:
          </label>
          <select
            id="sort"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-2 py-1 text-xs border border-gray-300 rounded-md bg-white text-text-primary focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="status">Status</option>
            <option value="name">Name</option>
            <option value="region">Region</option>
          </select>
        </div>
      </div>

      {/* River List */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-4 space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="bg-gray-100 rounded-lg h-20 animate-pulse" />
            ))}
          </div>
        ) : rivers.length === 0 ? (
          <div className="p-4 text-center">
            <p className="text-text-muted">No rivers available</p>
          </div>
        ) : (
          <div className="p-4 space-y-3">
            {sortedRivers.map((river) => (
              <RiverCard
                key={river.id}
                river={river}
                isSelected={selectedRiverId === river.id}
                onClick={onSelectRiver}
              />
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 flex-shrink-0 text-xs text-text-muted space-y-1">
        <p>Data from USGS & CDEC · Provisional</p>
        <p>Not for safety decisions</p>
      </div>
    </div>
  )
}
