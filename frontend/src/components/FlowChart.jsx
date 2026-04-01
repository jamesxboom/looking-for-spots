import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'

export default function FlowChart({ data, greenFloor, greenCeiling, status }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
        <p className="text-text-muted">No data available</p>
      </div>
    )
  }

  const statusColors = {
    green: '#22c55e',
    yellow: '#eab308',
    red: '#ef4444',
  }

  const chartData = data.map((point) => ({
    ...point,
    timestamp: new Date(point.timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    }),
    cfs: point.cfs || point.flow || 0,
  }))

  const fillColor = statusColors[status] || statusColors.green
  const fillOpacity = 0.2

  return (
    <div className="w-full h-64 bg-white rounded-lg border border-gray-200 p-4">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id={`gradient-${status}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={fillColor} stopOpacity={fillOpacity} />
              <stop offset="95%" stopColor={fillColor} stopOpacity={0} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            dataKey="timestamp"
            stroke="#94a3b8"
            style={{ fontSize: '12px' }}
            interval={Math.max(0, Math.floor(data.length / 4) - 1)}
          />
          <YAxis
            stroke="#94a3b8"
            style={{ fontSize: '12px' }}
            label={{ value: 'CFS', angle: -90, position: 'insideLeft' }}
          />

          {greenFloor && greenCeiling && (
            <>
              <ReferenceLine
                y={greenFloor}
                stroke="#22c55e"
                strokeDasharray="5 5"
                opacity={0.5}
                label={{
                  value: `Floor: ${greenFloor}`,
                  position: 'right',
                  fill: '#22c55e',
                  fontSize: 12,
                }}
              />
              <ReferenceLine
                y={greenCeiling}
                stroke="#22c55e"
                strokeDasharray="5 5"
                opacity={0.5}
                label={{
                  value: `Ceiling: ${greenCeiling}`,
                  position: 'right',
                  fill: '#22c55e',
                  fontSize: 12,
                }}
              />
            </>
          )}

          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
            }}
            formatter={(value) => [value?.toLocaleString() + ' cfs', 'Flow']}
          />

          <Area
            type="monotone"
            dataKey="cfs"
            stroke={fillColor}
            strokeWidth={2}
            fill={`url(#gradient-${status})`}
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
