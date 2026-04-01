import StatusBadge from './StatusBadge'
import TrendArrow from './TrendArrow'

export default function RiverCard({
  river,
  isSelected = false,
  onClick,
}) {
  const statusDotColors = {
    green: 'bg-status-green',
    yellow: 'bg-status-yellow',
    red: 'bg-status-red',
  }

  const statusDot = statusDotColors[river.status] || statusDotColors.yellow
  const isDualMode = river.modeStatuses && river.modeStatuses.length > 1

  const handleClick = () => {
    if (onClick) onClick(river.id)
  }

  return (
    <button
      onClick={handleClick}
      className={`w-full text-left p-4 rounded-lg border transition-all duration-200 ${
        isSelected
          ? 'bg-white border-2 border-blue-500 shadow-lg'
          : 'bg-white border border-gray-200 hover:shadow-md hover:border-gray-300'
      }`}
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-start gap-3 flex-1">
          <div className={`${statusDot} rounded-full w-3 h-3 flex-shrink-0 mt-1`} />
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-text-primary truncate text-sm">
              {river.name}
            </h3>
            <p className="text-xs text-text-muted mt-1">
              {river.currentCfs?.toLocaleString() || '—'} cfs
            </p>
          </div>
        </div>
        <StatusBadge status={river.status} />
      </div>

      {/* Dual-mode mini indicators */}
      {isDualMode && (
        <div className="flex items-center gap-3 mt-2 mb-1">
          {river.modeStatuses.map((ms) => (
            <div key={ms.mode} className="flex items-center gap-1.5">
              <div className={`${statusDotColors[ms.status] || 'bg-gray-400'} rounded-full w-2 h-2`} />
              <span className="text-xs text-text-muted capitalize">
                {ms.mode === 'drift' ? 'Drift' : ms.mode}
              </span>
            </div>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between gap-2 text-xs mt-3">
        <span className="text-text-muted">
          {river.waterTempF ? (
            <span className={river.waterTempF >= 68 ? 'text-status-red font-semibold' : river.waterTempF >= 65 ? 'text-status-yellow font-semibold' : ''}>
              {river.waterTempF}°F
            </span>
          ) : '—'}
        </span>
        <TrendArrow trend={river.trend} change={river.cfsChange6hr} />
      </div>

      {river.statusReason && (
        <p className="text-xs text-text-muted mt-2 line-clamp-2">
          {river.statusReason}
        </p>
      )}
    </button>
  )
}
