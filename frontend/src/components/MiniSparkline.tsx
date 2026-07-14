import type { TrendPoint } from '../types'

export function MiniSparkline({
  points,
  color = '#2dd4bf',
  className = '',
}: {
  points: TrendPoint[]
  color?: string
  className?: string
}) {
  const scores = points
    .map((point) => point.health_score)
    .filter((score) => Number.isFinite(score))

  if (scores.length < 2) {
    return (
      <svg aria-hidden="true" className={className} height="28" viewBox="0 0 120 28" width="120">
        <line x1="0" y1="14" x2="120" y2="14" stroke={color} strokeOpacity="0.35" strokeWidth="2" />
      </svg>
    )
  }

  const min = Math.min(...scores)
  const max = Math.max(...scores)
  const range = Math.max(max - min, 1)
  const path = scores
    .map((score, index) => {
      const x = (index / (scores.length - 1)) * 120
      const y = 24 - ((score - min) / range) * 20
      return `${index === 0 ? 'M' : 'L'}${x.toFixed(1)} ${y.toFixed(1)}`
    })
    .join(' ')

  return (
    <svg aria-hidden="true" className={className} height="28" role="img" viewBox="0 0 120 28" width="120">
      <path d={path} fill="none" stroke={color} strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
    </svg>
  )
}
