import { useState } from 'react';
import './GoalWizard.css';

/**
 * Multi-step goal creation wizard.
 * Step 1: Goal title + optional deadline.
 * Step 2: Add tasks (each can have subtasks).
 * Step 3: Review and create.
 */
export default function GoalWizard({ onSave, onCancel, editGoal }) {
  const [step, setStep] = useState(1);
  const [title, setTitle] = useState(editGoal?.title || '');
  const [deadline, setDeadline] = useState(editGoal?.deadline || '');
  const [hasCustomDeadline, setHasCustomDeadline] = useState(editGoal?.has_custom_deadline || false);
  const [tasks, setTasks] = useState(editGoal?.tasks || []);
  const [newTaskTitle, setNewTaskTitle] = useState('');

  const addTask = () => {
    if (!newTaskTitle.trim()) return;
    setTasks([...tasks, {
      id: crypto.randomUUID(),
      title: newTaskTitle.trim(),
      position: tasks.length,
      is_completed: false,
      created_at: new Date().toISOString(),
      sub_tasks: [],
    }]);
    setNewTaskTitle('');
  };

  const removeTask = (idx) => {
    setTasks(tasks.filter((_, i) => i !== idx).map((t, i) => ({ ...t, position: i })));
  };

  const addSubtask = (taskIdx, subtaskTitle) => {
    if (!subtaskTitle.trim()) return;
    const updated = [...tasks];
    updated[taskIdx] = {
      ...updated[taskIdx],
      sub_tasks: [
        ...updated[taskIdx].sub_tasks,
        {
          id: crypto.randomUUID(),
          title: subtaskTitle.trim(),
          position: updated[taskIdx].sub_tasks.length,
          is_completed: false,
          created_at: new Date().toISOString(),
        },
      ],
    };
    setTasks(updated);
  };

  const removeSubtask = (taskIdx, stIdx) => {
    const updated = [...tasks];
    updated[taskIdx] = {
      ...updated[taskIdx],
      sub_tasks: updated[taskIdx].sub_tasks
        .filter((_, i) => i !== stIdx)
        .map((st, i) => ({ ...st, position: i })),
    };
    setTasks(updated);
  };

  const handleSave = () => {
    if (!title.trim()) return;
    onSave({
      title: title.trim(),
      deadline: hasCustomDeadline && deadline ? deadline : null,
      has_custom_deadline: hasCustomDeadline,
      tasks,
    });
  };

  const canProceed = step === 1 ? title.trim().length > 0 : true;

  return (
    <div className="wizard-overlay" onClick={onCancel}>
      <div className="wizard-modal" onClick={(e) => e.stopPropagation()}>
        <div className="wizard-header">
          <h2>{editGoal ? 'Edit Goal' : 'New Goal'}</h2>
          <div className="wizard-steps">
            {[1, 2, 3].map((s) => (
              <div key={s} className={`step-dot ${step >= s ? 'active' : ''}`} />
            ))}
          </div>
          <button className="icon-btn" onClick={onCancel}>✕</button>
        </div>

        <div className="wizard-body">
          {step === 1 && (
            <div className="wizard-step">
              <label className="field-label">What do you want to achieve?</label>
              <input
                className="wizard-input"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Learn Rust properly"
                autoFocus
              />

              <label className="field-label" style={{ marginTop: 'var(--space-5)' }}>
                <input
                  type="checkbox"
                  checked={hasCustomDeadline}
                  onChange={(e) => setHasCustomDeadline(e.target.checked)}
                />
                {' '}Set a custom deadline
              </label>

              {hasCustomDeadline && (
                <input
                  type="datetime-local"
                  className="wizard-input"
                  value={deadline}
                  onChange={(e) => setDeadline(e.target.value)}
                />
              )}
            </div>
          )}

          {step === 2 && (
            <div className="wizard-step">
              <label className="field-label">Break it into tasks</label>
              <div className="wizard-task-list">
                {tasks.map((task, taskIdx) => (
                  <TaskInput
                    key={task.id}
                    task={task}
                    taskIdx={taskIdx}
                    onRemove={() => removeTask(taskIdx)}
                    onAddSubtask={(title) => addSubtask(taskIdx, title)}
                    onRemoveSubtask={(stIdx) => removeSubtask(taskIdx, stIdx)}
                  />
                ))}
              </div>
              <div className="wizard-add-row">
                <input
                  className="wizard-input"
                  placeholder="Add a task..."
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && addTask()}
                />
                <button className="add-btn" onClick={addTask}>Add</button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="wizard-step">
              <label className="field-label">Review</label>
              <div className="review-card">
                <h3>{title}</h3>
                {hasCustomDeadline && deadline && (
                  <p className="review-meta">Deadline: {new Date(deadline).toLocaleString()}</p>
                )}
                {tasks.length > 0 && (
                  <ul className="review-tasks">
                    {tasks.map((t) => (
                      <li key={t.id}>
                        {t.title}
                        {t.sub_tasks.length > 0 && (
                          <ul>
                            {t.sub_tasks.map((st) => <li key={st.id}>{st.title}</li>)}
                          </ul>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
                {tasks.length === 0 && <p className="review-meta">No tasks added yet</p>}
              </div>
            </div>
          )}
        </div>

        <div className="wizard-footer">
          {step > 1 && (
            <button className="wizard-btn secondary" onClick={() => setStep(step - 1)}>Back</button>
          )}
          <div style={{ flex: 1 }} />
          {step < 3 ? (
            <button
              className="wizard-btn primary"
              onClick={() => setStep(step + 1)}
              disabled={!canProceed}
            >
              Next
            </button>
          ) : (
            <button
              className="wizard-btn primary"
              onClick={handleSave}
              disabled={!title.trim()}
            >
              {editGoal ? 'Save Changes' : 'Create Goal'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}


function TaskInput({ task, taskIdx, onRemove, onAddSubtask, onRemoveSubtask }) {
  const [subtaskTitle, setSubtaskTitle] = useState('');

  const handleAdd = () => {
    onAddSubtask(subtaskTitle);
    setSubtaskTitle('');
  };

  return (
    <div className="wizard-task-item">
      <div className="wizard-task-header">
        <span className="wizard-task-num">{taskIdx + 1}.</span>
        <span className="wizard-task-title">{task.title}</span>
        <button className="icon-btn small danger" onClick={onRemove}>✕</button>
      </div>
      {task.sub_tasks.map((st, stIdx) => (
        <div key={st.id} className="wizard-subtask-row">
          <span className="wizard-subtask-dot">·</span>
          <span>{st.title}</span>
          <button className="icon-btn tiny danger" onClick={() => onRemoveSubtask(stIdx)}>✕</button>
        </div>
      ))}
      <div className="wizard-subtask-add">
        <input
          placeholder="Add subtask..."
          value={subtaskTitle}
          onChange={(e) => setSubtaskTitle(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
        />
        <button className="add-btn small" onClick={handleAdd}>+</button>
      </div>
    </div>
  );
}
