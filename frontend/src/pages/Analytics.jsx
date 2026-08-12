import { useCallback } from 'react';
import { useApi } from '../hooks/useApi';
import { analytics as analyticsApi } from '../services/api';
import StatCard from '../components/StatCard';
import './Analytics.css';

/**
 * Analytics page — performance metrics for goals and task list.
 */
export default function Analytics() {
  const { data: goalStats, loading: gl } = useApi(
    useCallback(() => analyticsApi.goals(), []),
    []
  );
  const { data: tlStats, loading: tl } = useApi(
    useCallback(() => analyticsApi.taskList(), []),
    []
  );

  if (gl || tl) return <div className="page-loading">Loading...</div>;

  const summary = goalStats?.summary || {};
  const performance = goalStats?.performance || {};
  const recentGoals = goalStats?.recent_goals || [];
  const tagBreakdown = tlStats?.tag_breakdown || {};

  const formatDuration = (seconds) => {
    if (!seconds) return '—';
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    if (hours > 24) return `${Math.floor(hours / 24)}d`;
    if (hours > 0) return `${hours}h ${mins}m`;
    return `${mins}m`;
  };

  return (
    <div className="analytics-page">
      <h1>Analytics</h1>

      {/* Goal stats */}
      <section className="analytics-section">
        <h2 className="section-title">Goals</h2>
        <div className="stats-grid">
          <StatCard label="Total" value={summary.total ?? 0} accent="teal" />
          <StatCard label="Active" value={summary.active ?? 0} accent="amber" />
          <StatCard label="Completed" value={summary.completed ?? 0} accent="green" />
          <StatCard label="Overdue" value={summary.overdue ?? 0} accent="red" />
        </div>
      </section>

      {/* Performance */}
      <section className="analytics-section">
        <h2 className="section-title">Performance</h2>
        <div className="stats-grid">
          <StatCard
            label="Completion"
            value={`${performance.completion_pct ?? 0}%`}
            accent="teal"
          />
          {performance.has_custom_deadlines && (
            <StatCard
              label="On-Time"
              value={`${performance.on_time_pct ?? 0}%`}
              subtitle="custom deadlines"
              accent="green"
            />
          )}
          {performance.has_default_deadlines && (
            <StatCard
              label="Same-Day"
              value={`${performance.same_day_pct ?? 0}%`}
              subtitle="default deadlines"
              accent="purple"
            />
          )}
        </div>
      </section>

      {/* Task list stats */}
      <section className="analytics-section">
        <h2 className="section-title">Task List</h2>
        <div className="stats-grid">
          <StatCard label="Active" value={tlStats?.active_count ?? 0} accent="amber" />
          <StatCard label="Completed" value={tlStats?.completed_count ?? 0} accent="green" />
          <StatCard
            label="Avg Time"
            value={formatDuration(tlStats?.avg_time_seconds)}
            subtitle="in queue"
            accent="purple"
          />
        </div>
      </section>

      {/* Tag breakdown */}
      {Object.keys(tagBreakdown).length > 0 && (
        <section className="analytics-section">
          <h2 className="section-title">Tags</h2>
          <div className="tag-breakdown">
            {Object.entries(tagBreakdown).map(([tag, count]) => (
              <div key={tag} className="tag-bar">
                <span className="tag-bar-label">{tag}</span>
                <div className="tag-bar-track">
                  <div
                    className="tag-bar-fill"
                    style={{
                      width: `${Math.min(100, (count / Math.max(...Object.values(tagBreakdown))) * 100)}%`,
                    }}
                  />
                </div>
                <span className="tag-bar-count">{count}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Recent goals */}
      {recentGoals.length > 0 && (
        <section className="analytics-section">
          <h2 className="section-title">Recent Goals</h2>
          <div className="recent-goals">
            {recentGoals.map((g) => (
              <div key={g.id} className="recent-goal-item">
                <div className="recent-goal-info">
                  <span className={`recent-goal-title ${g.is_completed ? 'done' : ''}`}>
                    {g.title}
                  </span>
                  <div className="recent-goal-meta">
                    <span>{g.completion_pct}%</span>
                    {g.is_overdue && <span className="text-red">overdue</span>}
                    {g.on_time === true && <span className="text-green">on time ✓</span>}
                    {g.same_day === true && <span className="text-purple">same day ✓</span>}
                  </div>
                </div>
                <div className="recent-goal-bar">
                  <div
                    className="recent-goal-fill"
                    style={{
                      width: `${g.completion_pct}%`,
                      background: g.is_completed ? 'var(--teal)' : g.is_overdue ? 'var(--red)' : 'var(--amber)',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
