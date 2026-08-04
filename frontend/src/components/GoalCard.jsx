import { useState } from 'react';
import './GoalCard.css';

/**
 * Hierarchical goal card with expandable tasks and subtasks.
 * Handles inline editing, completion toggling, and CRUD actions.
 */
export default function GoalCard({
  goal,
  expanded,
  onExpand,
  onToggleGoal,
  onToggleTask,
  onToggleSubtask,
  onDeleteGoal,
  onEditGoal,
  onEditTask,
  onEditSubtask,
  onDeleteTask,
  onDeleteSubtask,
  onMoveTask,
  onMoveSubtask,
  onAddTask,
  onAddSubtask,
  onChangeDeadline,
}) {
  const [editingGoalTitle, setEditingGoalTitle] = useState(false);
  const [goalTitle, setGoalTitle] = useState(goal.title);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newSubtaskFor, setNewSubtaskFor] = useState(null);
  const [newSubtaskTitle, setNewSubtaskTitle] = useState('');
  const [editingTaskId, setEditingTaskId] = useState(null);
  const [editTaskTitle, setEditTaskTitle] = useState('');
  const [editingSubtaskId, setEditingSubtaskId] = useState(null);
  const [editSubtaskTitle, setEditSubtaskTitle] = useState('');

  const pct = goal.completion_percentage ?? 0;
  const isOverdue = goal.deadline && !goal.is_completed && new Date(goal.deadline) < new Date();

  const handleGoalTitleSave = () => {
    if (goalTitle.trim() && goalTitle !== goal.title) {
      onEditGoal(goal.id, goalTitle.trim());
    }
    setEditingGoalTitle(false);
  };

  const handleAddTask = () => {
    if (newTaskTitle.trim()) {
      onAddTask(goal.id, newTaskTitle.trim());
      setNewTaskTitle('');
    }
  };

  const handleAddSubtask = (taskId) => {
    if (newSubtaskTitle.trim()) {
      onAddSubtask(goal.id, taskId, newSubtaskTitle.trim());
      setNewSubtaskTitle('');
      setNewSubtaskFor(null);
    }
  };

  const handleEditTaskSave = (taskId) => {
    if (editTaskTitle.trim()) {
      onEditTask(goal.id, taskId, editTaskTitle.trim());
    }
    setEditingTaskId(null);
  };

  const handleEditSubtaskSave = (taskId, subtaskId) => {
    if (editSubtaskTitle.trim()) {
      onEditSubtask(goal.id, taskId, subtaskId, editSubtaskTitle.trim());
    }
    setEditingSubtaskId(null);
  };

  return (
    <div className={`goal-card ${goal.is_completed ? 'completed' : ''} ${isOverdue ? 'overdue' : ''}`}>
      {/* Header */}
      <div className="goal-header" onClick={() => onExpand(goal.id)}>
        <button
          className="goal-checkbox"
          onClick={(e) => { e.stopPropagation(); onToggleGoal(goal.id, !goal.is_completed); }}
          title={goal.is_completed ? 'Mark incomplete' : 'Mark complete'}
        >
          {goal.is_completed ? '✓' : '○'}
        </button>

        <div className="goal-info">
          {editingGoalTitle ? (
            <input
              className="inline-edit"
              value={goalTitle}
              onChange={(e) => setGoalTitle(e.target.value)}
              onBlur={handleGoalTitleSave}
              onKeyDown={(e) => e.key === 'Enter' && handleGoalTitleSave()}
              onClick={(e) => e.stopPropagation()}
              autoFocus
            />
          ) : (
            <h3
              className={`goal-title ${goal.is_completed ? 'done' : ''}`}
              onDoubleClick={(e) => { e.stopPropagation(); setEditingGoalTitle(true); }}
            >
              {goal.title}
            </h3>
          )}

          <div className="goal-meta">
            {goal.tasks.length > 0 && (
              <span className="meta-chip">{pct}%</span>
            )}
            {isOverdue && <span className="meta-chip overdue-chip">overdue</span>}
            {goal.tasks.length > 0 && (
              <span className="meta-chip">{goal.tasks.filter(t => t.is_completed).length}/{goal.tasks.length} tasks</span>
            )}
          </div>
        </div>

        <div className="goal-actions">
          <button className="icon-btn" onClick={(e) => { e.stopPropagation(); onChangeDeadline(goal.id); }} title="Set deadline">⏱</button>
          <button className="icon-btn" onClick={(e) => { e.stopPropagation(); setEditingGoalTitle(true); }} title="Edit">✎</button>
          <button className="icon-btn danger" onClick={(e) => { e.stopPropagation(); onDeleteGoal(goal.id); }} title="Delete">✕</button>
          <span className="expand-icon">{expanded ? '▾' : '▸'}</span>
        </div>
      </div>

      {/* Progress bar */}
      {goal.tasks.length > 0 && (
        <div className="progress-track">
          <div
            className="progress-fill"
            style={{
              width: `${pct}%`,
              background: goal.is_completed ? 'var(--teal)' : isOverdue ? 'var(--red)' : 'var(--amber)',
            }}
          />
        </div>
      )}

      {/* Expanded content */}
      {expanded && (
        <div className="goal-body">
          {goal.tasks.map((task, taskIdx) => (
            <div key={task.id} className={`task-item ${task.is_completed ? 'completed' : ''}`}>
              <div className="task-row">
                <button
                  className="task-checkbox"
                  onClick={() => onToggleTask(goal.id, task.id, !task.is_completed)}
                >
                  {task.is_completed ? '✓' : '○'}
                </button>

                {editingTaskId === task.id ? (
                  <input
                    className="inline-edit"
                    value={editTaskTitle}
                    onChange={(e) => setEditTaskTitle(e.target.value)}
                    onBlur={() => handleEditTaskSave(task.id)}
                    onKeyDown={(e) => e.key === 'Enter' && handleEditTaskSave(task.id)}
                    autoFocus
                  />
                ) : (
                  <span
                    className={`task-title ${task.is_completed ? 'done' : ''}`}
                    onDoubleClick={() => { setEditingTaskId(task.id); setEditTaskTitle(task.title); }}
                  >
                    {task.title}
                  </span>
                )}

                <div className="task-actions">
                  {taskIdx > 0 && (
                    <button className="icon-btn small" onClick={() => onMoveTask(goal.id, task.id, -1)} title="Move up">↑</button>
                  )}
                  {taskIdx < goal.tasks.length - 1 && (
                    <button className="icon-btn small" onClick={() => onMoveTask(goal.id, task.id, 1)} title="Move down">↓</button>
                  )}
                  <button className="icon-btn small" onClick={() => { setNewSubtaskFor(task.id); setNewSubtaskTitle(''); }} title="Add subtask">+</button>
                  <button className="icon-btn small danger" onClick={() => onDeleteTask(goal.id, task.id)} title="Delete">✕</button>
                </div>
              </div>

              {/* Subtasks */}
              {task.sub_tasks.map((st, stIdx) => (
                <div key={st.id} className={`subtask-row ${st.is_completed ? 'completed' : ''}`}>
                  <button
                    className="subtask-checkbox"
                    onClick={() => onToggleSubtask(goal.id, task.id, st.id, !st.is_completed)}
                  >
                    {st.is_completed ? '✓' : '·'}
                  </button>

                  {editingSubtaskId === st.id ? (
                    <input
                      className="inline-edit small"
                      value={editSubtaskTitle}
                      onChange={(e) => setEditSubtaskTitle(e.target.value)}
                      onBlur={() => handleEditSubtaskSave(task.id, st.id)}
                      onKeyDown={(e) => e.key === 'Enter' && handleEditSubtaskSave(task.id, st.id)}
                      autoFocus
                    />
                  ) : (
                    <span
                      className={`subtask-title ${st.is_completed ? 'done' : ''}`}
                      onDoubleClick={() => { setEditingSubtaskId(st.id); setEditSubtaskTitle(st.title); }}
                    >
                      {st.title}
                    </span>
                  )}

                  <div className="subtask-actions">
                    {stIdx > 0 && (
                      <button className="icon-btn tiny" onClick={() => onMoveSubtask(goal.id, task.id, st.id, -1)}>↑</button>
                    )}
                    {stIdx < task.sub_tasks.length - 1 && (
                      <button className="icon-btn tiny" onClick={() => onMoveSubtask(goal.id, task.id, st.id, 1)}>↓</button>
                    )}
                    <button className="icon-btn tiny danger" onClick={() => onDeleteSubtask(goal.id, task.id, st.id)}>✕</button>
                  </div>
                </div>
              ))}

              {/* Inline add subtask */}
              {newSubtaskFor === task.id && (
                <div className="inline-add subtask-level">
                  <input
                    placeholder="Add subtask..."
                    value={newSubtaskTitle}
                    onChange={(e) => setNewSubtaskTitle(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAddSubtask(task.id)}
                    autoFocus
                  />
                  <button className="add-btn" onClick={() => handleAddSubtask(task.id)}>Add</button>
                  <button className="cancel-btn" onClick={() => setNewSubtaskFor(null)}>Cancel</button>
                </div>
              )}
            </div>
          ))}

          {/* Inline add task */}
          <div className="inline-add">
            <input
              placeholder="Add task..."
              value={newTaskTitle}
              onChange={(e) => setNewTaskTitle(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAddTask()}
            />
            <button className="add-btn" onClick={handleAddTask}>Add</button>
          </div>
        </div>
      )}
    </div>
  );
}
