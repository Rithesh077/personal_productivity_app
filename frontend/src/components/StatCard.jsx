import './StatCard.css';

/**
 * Reusable metric card for analytics dashboards.
 * Shows a label, value, and optional subtitle/accent color.
 */
export default function StatCard({ label, value, subtitle, accent = 'teal' }) {
  const accentVar = `var(--${accent})`;
  const accentMuted = `var(--${accent}-muted)`;

  return (
    <div className="stat-card" style={{ '--accent': accentVar, '--accent-muted': accentMuted }}>
      <span className="stat-label">{label}</span>
      <span className="stat-value">{value}</span>
      {subtitle && <span className="stat-subtitle">{subtitle}</span>}
    </div>
  );
}
