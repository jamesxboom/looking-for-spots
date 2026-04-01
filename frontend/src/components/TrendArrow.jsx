export default function TrendArrow({ trend, change, trendContext }) {
  // For fly fishing: falling/clearing = GOOD, rising/muddying = BAD
  const trendConfig = {
    rising: { symbol: '↑', color: 'text-status-red', label: 'Rising' },
    stable: { symbol: '→', color: 'text-status-green', label: 'Stable' },
    falling: { symbol: '↓', color: 'text-blue-500', label: 'Falling' },
  }

  const config = trendConfig[trend] || trendConfig.stable

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-2">
        <span className={`text-lg font-bold ${config.color}`}>{config.symbol}</span>
        <span className="text-sm text-text-muted">
          {config.label}
          {change !== undefined && change !== null && (
            <span className="ml-1 font-medium">
              {change > 0 ? '+' : ''}{change.toLocaleString()} cfs
            </span>
          )}
        </span>
      </div>
      {trendContext && (
        <p className="text-xs text-text-muted italic">{trendContext}</p>
      )}
    </div>
  )
}
