export default function StatusBadge({ status }) {
  const statusConfig = {
    green: {
      bg: 'bg-bg-green',
      text: 'text-status-green',
      label: 'FISH ON'
    },
    yellow: {
      bg: 'bg-bg-yellow',
      text: 'text-status-yellow',
      label: 'CAUTION'
    },
    red: {
      bg: 'bg-bg-red',
      text: 'text-status-red',
      label: 'NO GO'
    }
  }

  const config = statusConfig[status] || statusConfig.yellow

  return (
    <div className={`${config.bg} ${config.text} px-3 py-1 rounded-full text-xs font-semibold inline-block`}>
      {config.label}
    </div>
  )
}
