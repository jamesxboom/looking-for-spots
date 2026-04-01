import StatusBadge from './StatusBadge'
import TrendArrow from './TrendArrow'
import FlowChart from './FlowChart'
import { useRiverDetail, useRiverHistory } from '../hooks/useRivers'

// Temperature thresholds for trout
const TEMP_DANGER_F = 68
const TEMP_WARNING_F = 65

function TempIndicator({ tempF }) {
  if (tempF === null || tempF === undefined) return null

  let color = 'text-status-green'
  let bg = 'bg-bg-green'
  let label = 'Good for trout'

  if (tempF >= TEMP_DANGER_F) {
    color = 'text-status-red'
    bg = 'bg-bg-red'
    label = 'Trout stress — stop fishing'
  } else if (tempF >= TEMP_WARNING_F) {
    color = 'text-status-yellow'
    bg = 'bg-bg-yellow'
    label = 'Warming — fish early morning'
  }

  return (
    <div className={`${bg} rounded-lg px-3 py-2 mt-2`}>
      <span className={`text-xs font-semibold ${color}`}>{label}</span>
    </div>
  )
}

function ModeStatusBadge({ mode, status }) {
  const modeLabels = { wade: 'Wade', drift: 'Drift Boat', boat: 'Boat' }
  const statusDotColors = {
    green: 'bg-status-green',
    yellow: 'bg-status-yellow',
    red: 'bg-status-red',
  }

  return (
    <div className="flex items-center gap-2">
      <div className={`${statusDotColors[status] || 'bg-gray-400'} rounded-full w-2.5 h-2.5`} />
      <span className="text-sm font-medium text-text-primary">
        {modeLabels[mode] || mode}
      </span>
    </div>
  )
}

export default function RiverDetail({ riverId, onBack }) {
  const { river, loading: detailLoading } = useRiverDetail(riverId)
  const { history, loading: historyLoading } = useRiverHistory(riverId, 7)

  if (detailLoading) {
    return (
      <div className="h-full bg-white rounded-lg p-6 overflow-y-auto flex items-center justify-center">
        <p className="text-text-muted">Loading river details...</p>
      </div>
    )
  }

  if (!river) {
    return (
      <div className="h-full bg-white rounded-lg p-6 overflow-y-auto flex items-center justify-center">
        <p className="text-text-muted">River data not available</p>
      </div>
    )
  }

  const optimalFloor = river.thresholds?.greenFloor
  const optimalCeiling = river.thresholds?.greenCeiling
  const isDualMode = river.modeStatuses && river.modeStatuses.length > 1

  return (
    <div className="h-full bg-white rounded-lg p-6 overflow-y-auto flex flex-col">
      {/* Header */}
      <div className="mb-6 pb-6 border-b border-gray-200">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium text-sm mb-4 transition"
        >
          ← Back to Map
        </button>

        <h2 className="text-2xl font-bold text-text-primary mb-3">{river.name}</h2>

        <div className="flex items-center gap-3">
          <StatusBadge status={river.status} />
          <p className="text-sm text-text-muted">{river.statusReason || 'Check conditions'}</p>
        </div>
      </div>

      {/* Dual-Mode Statuses */}
      {isDualMode && (
        <div className="mb-6 pb-6 border-b border-gray-200">
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wide mb-3">
            Fishing Mode Status
          </h3>
          <div className="space-y-3">
            {river.modeStatuses.map((ms) => (
              <div key={ms.mode} className="bg-bg-light rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <ModeStatusBadge mode={ms.mode} status={ms.status} />
                  <StatusBadge status={ms.status} />
                </div>
                <p className="text-xs text-text-muted mt-1">{ms.statusReason}</p>
                {ms.thresholds && (
                  <p className="text-xs text-text-muted mt-1">
                    Optimal: {ms.thresholds.greenFloor?.toLocaleString()}–{ms.thresholds.greenCeiling?.toLocaleString()} cfs
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Current Flow Section */}
      <div className="mb-6 pb-6 border-b border-gray-200">
        <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wide mb-3">
          Current Flow
        </h3>

        <div className="mb-4">
          <div className="text-3xl font-bold text-text-primary mb-1">
            {river.currentCfs?.toLocaleString() || '—'} cfs
          </div>
          <p className="text-sm text-text-muted">Current discharge</p>
        </div>

        {optimalFloor && optimalCeiling && (
          <div className="bg-bg-light rounded-lg p-4">
            <p className="text-xs text-text-muted mb-2">
              Optimal Range{isDualMode ? ' (default)' : ''}
            </p>
            <div className="text-lg font-semibold text-text-primary">
              {optimalFloor?.toLocaleString()} — {optimalCeiling?.toLocaleString()} cfs
            </div>
            <div className="mt-3 bg-white rounded h-2 overflow-hidden">
              <div
                className="h-full bg-status-green"
                style={{
                  width: `${
                    Math.min(
                      100,
                      Math.max(
                        0,
                        ((river.currentCfs - optimalFloor) /
                          (optimalCeiling - optimalFloor)) *
                          100
                      )
                    ) || 0
                  }%`,
                }}
              />
            </div>
          </div>
        )}

        {/* Blown out / danger warnings */}
        {river.blownOutCfs && (
          <p className="text-xs text-status-red mt-2 font-medium">
            Blown out above {river.blownOutCfs.toLocaleString()} cfs
          </p>
        )}
        {river.dangerousWadeCfs && (
          <p className="text-xs text-status-yellow mt-1 font-medium">
            Wading dangerous above {river.dangerousWadeCfs.toLocaleString()} cfs
          </p>
        )}
      </div>

      {/* Temperature & Trend */}
      <div className="mb-6 pb-6 border-b border-gray-200 grid grid-cols-2 gap-4">
        <div>
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wide mb-2">
            Water Temperature
          </h3>
          <div className="text-2xl font-bold text-text-primary">
            {river.waterTempF ? `${river.waterTempF}°F` : '—'}
          </div>
          <p className="text-xs text-text-muted mt-1">
            {TEMP_DANGER_F}°F = trout stress threshold
          </p>
          <TempIndicator tempF={river.waterTempF} />
        </div>

        <div>
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wide mb-2">
            Trend
          </h3>
          <TrendArrow
            trend={river.trend}
            change={river.cfsChange6hr}
            trendContext={river.trendContext}
          />
          <p className="text-xs text-text-muted mt-2">
            {river.cfsChange6hr !== undefined
              ? `${Math.abs(river.cfsChange6hr)?.toLocaleString()} cfs in 6 hours`
              : 'Data unavailable'}
          </p>
        </div>
      </div>

      {/* 7-Day Chart */}
      <div className="mb-6">
        <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wide mb-3">
          7-Day Flow Trend
        </h3>
        {historyLoading ? (
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
            <p className="text-text-muted">Loading chart...</p>
          </div>
        ) : (
          <FlowChart
            data={history}
            greenFloor={optimalFloor}
            greenCeiling={optimalCeiling}
            status={river.status}
          />
        )}
      </div>

      {/* River Info */}
      <div className="mb-6 pb-6 border-b border-gray-200">
        <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wide mb-3">
          River Information
        </h3>
        <div className="space-y-3 text-sm">
          <div>
            <p className="text-text-muted">Type</p>
            <p className="font-medium text-text-primary capitalize">
              {river.riverType || 'Unknown'}
            </p>
          </div>
          {river.fishingModes && (
            <div>
              <p className="text-text-muted">Fishing Modes</p>
              <p className="font-medium text-text-primary capitalize">
                {river.fishingModes.join(', ').replace('drift', 'drift boat')}
              </p>
            </div>
          )}
          {river.notes && (
            <div>
              <p className="text-text-muted">Notes</p>
              <p className="font-medium text-text-primary">{river.notes}</p>
            </div>
          )}
        </div>
      </div>

      {/* Attribution */}
      <div className="mt-auto text-xs text-text-muted space-y-1">
        <p>Gauge: {river.gaugeId || 'USGS'}</p>
        <p>Last updated: {river.updatedAt ? new Date(river.updatedAt).toLocaleString() : '—'}</p>
        <p className="pt-3 border-t border-gray-200">
          Data is provisional and not for safety decisions. Water temp above 68°F = stop fishing (trout stress).
        </p>
      </div>
    </div>
  )
}
