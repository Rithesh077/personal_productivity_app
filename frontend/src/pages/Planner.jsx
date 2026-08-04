import { useState, useCallback } from 'react';
import { useApi } from '../hooks/useApi';
import { goals as goalsApi, tasks as tasksApi, subtasks as subtasksApi } from '../services/api';
import GoalCard from '../components/GoalCard';
import GoalWizard from '../components/GoalWizard';
import './Planner.css';

/**
 * Planner page — hierarchical goal management.
 * Uses GoalCard for display and GoalWizard for creation.
 */
export default function Planner() {
  const { data: goalsList, loading, error, refresh } = useApi(
    useCallback(() => goalsApi.list(), []),
    []
  );

  const [expandedGoal, setExpandedGoal] = useState(null);
  const [showWizard, setShowWizard] = useState(false);

  const handleExpand = (goalId) => {
    setExpandedGoal(expandedGoal === goalId ? null : goalId);
  };

  // ── Goal mutations ────────────────────────────

  const handleCreateGoal = async (data) => {
    await goalsApi.create(data);
    setShowWizard(false);
    refresh();
  };

  const handleToggleGoal = async (goalId, value) => {
    await goalsApi.complete(goalId, value);
    refresh();
  };

  const handleDeleteGoal = async (goalId) => {
    await goalsApi.delete(goalId);
    if (expandedGoal === goalId) setExpandedGoal(null);
    refresh();
  };

  const handleEditGoal = async (goalId, title) => {
    await goalsApi.update(goalId, { title });
    refresh();
  };

  const handleChangeDeadline = async (goalId) => {
    const deadline = prompt('Enter deadline (YYYY-MM-DDTHH:MM):');
    if (deadline !== null) {
      await goalsApi.deadline(goalId, {
        deadline: deadline || null,
        has_custom_deadline: !!deadline,
      });
      refresh();
    }
  };

  // ── Task mutations ────────────────────────────

  const handleAddTask = async (goalId, title) => {
    await tasksApi.add(goalId, title);
    refresh();
  };

  const handleToggleTask = async (goalId, taskId, value) => {
    await tasksApi.complete(goalId, taskId, value);
    refresh();
  };

  const handleEditTask = async (goalId, taskId, title) => {
    await tasksApi.update(goalId, taskId, title);
    refresh();
  };

  const handleDeleteTask = async (goalId, taskId) => {
    await tasksApi.delete(goalId, taskId);
    refresh();
  };

  const handleMoveTask = async (goalId, taskId, direction) => {
    await tasksApi.move(goalId, taskId, direction);
    refresh();
  };

  // ── Subtask mutations ─────────────────────────

  const handleAddSubtask = async (goalId, taskId, title) => {
    await subtasksApi.add(goalId, taskId, title);
    refresh();
  };

  const handleToggleSubtask = async (goalId, taskId, subtaskId, value) => {
    await subtasksApi.complete(goalId, taskId, subtaskId, value);
    refresh();
  };

  const handleEditSubtask = async (goalId, taskId, subtaskId, title) => {
    await subtasksApi.update(goalId, taskId, subtaskId, title);
    refresh();
  };

  const handleDeleteSubtask = async (goalId, taskId, subtaskId) => {
    await subtasksApi.delete(goalId, taskId, subtaskId);
    refresh();
  };

  const handleMoveSubtask = async (goalId, taskId, subtaskId, direction) => {
    await subtasksApi.move(goalId, taskId, subtaskId, direction);
    refresh();
  };

  if (loading) return <div className="page-loading">Loading...</div>;
  if (error) return <div className="page-error">Error: {error}</div>;

  const goals = goalsList || [];
  const activeGoals = goals.filter((g) => !g.is_completed);
  const completedGoals = goals.filter((g) => g.is_completed);

  return (
    <div className="planner-page">
      <div className="planner-header">
        <div>
          <h1>Goals</h1>
          <p className="planner-subtitle">
            {activeGoals.length} active · {completedGoals.length} completed
          </p>
        </div>
        <button className="create-btn" onClick={() => setShowWizard(true)}>
          + New Goal
        </button>
      </div>

      <div className="goals-list">
        {activeGoals.length === 0 && completedGoals.length === 0 && (
          <div className="empty-state">
            <p>No goals yet</p>
            <p className="text-muted">Create your first goal to get started</p>
          </div>
        )}

        {activeGoals.map((goal) => (
          <GoalCard
            key={goal.id}
            goal={goal}
            expanded={expandedGoal === goal.id}
            onExpand={handleExpand}
            onToggleGoal={handleToggleGoal}
            onToggleTask={handleToggleTask}
            onToggleSubtask={handleToggleSubtask}
            onDeleteGoal={handleDeleteGoal}
            onEditGoal={handleEditGoal}
            onEditTask={handleEditTask}
            onEditSubtask={handleEditSubtask}
            onDeleteTask={handleDeleteTask}
            onDeleteSubtask={handleDeleteSubtask}
            onMoveTask={handleMoveTask}
            onMoveSubtask={handleMoveSubtask}
            onAddTask={handleAddTask}
            onAddSubtask={handleAddSubtask}
            onChangeDeadline={handleChangeDeadline}
          />
        ))}

        {completedGoals.length > 0 && (
          <>
            <h2 className="section-divider">Completed</h2>
            {completedGoals.map((goal) => (
              <GoalCard
                key={goal.id}
                goal={goal}
                expanded={expandedGoal === goal.id}
                onExpand={handleExpand}
                onToggleGoal={handleToggleGoal}
                onToggleTask={handleToggleTask}
                onToggleSubtask={handleToggleSubtask}
                onDeleteGoal={handleDeleteGoal}
                onEditGoal={handleEditGoal}
                onEditTask={handleEditTask}
                onEditSubtask={handleEditSubtask}
                onDeleteTask={handleDeleteTask}
                onDeleteSubtask={handleDeleteSubtask}
                onMoveTask={handleMoveTask}
                onMoveSubtask={handleMoveSubtask}
                onAddTask={handleAddTask}
                onAddSubtask={handleAddSubtask}
                onChangeDeadline={handleChangeDeadline}
              />
            ))}
          </>
        )}
      </div>

      {showWizard && (
        <GoalWizard
          onSave={handleCreateGoal}
          onCancel={() => setShowWizard(false)}
        />
      )}
    </div>
  );
}
