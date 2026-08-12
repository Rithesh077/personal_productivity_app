import { useState, useCallback } from 'react';
import { useApi } from '../hooks/useApi';
import { taskList as taskListApi, tags as tagsApi } from '../services/api';
import TaskListCard from '../components/TaskListCard';
import './TaskList.css';

/**
 * Task List page — priority queue for immediate actions.
 * The DMN-rescue queue: "what should I do right now?"
 */
export default function TaskList() {
  const { data: items, loading, error, refresh } = useApi(
    useCallback(() => taskListApi.list(), []),
    []
  );
  const { data: completedData, refresh: refreshCompleted } = useApi(
    useCallback(() => taskListApi.listCompleted(), []),
    []
  );
  const { data: tagsData } = useApi(
    useCallback(() => tagsApi.list(), []),
    []
  );

  const [newTitle, setNewTitle] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [newTags, setNewTags] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showCompleted, setShowCompleted] = useState(false);

  const allTags = tagsData?.all || [];
  const completed = completedData || [];

  const handleCreate = async () => {
    if (!newTitle.trim()) return;
    await taskListApi.create({
      title: newTitle.trim(),
      description: newDescription.trim(),
      tags: newTags,
    });
    setNewTitle('');
    setNewDescription('');
    setNewTags([]);
    setShowAddForm(false);
    refresh();
  };

  const handleComplete = async (id) => {
    await taskListApi.complete(id);
    refresh();
    refreshCompleted();
  };

  const handleDelete = async (id) => {
    await taskListApi.delete(id);
    refresh();
  };

  const handleEdit = async (id, data) => {
    await taskListApi.update(id, data);
    refresh();
  };

  const handleClearCompleted = async () => {
    await taskListApi.clearCompleted();
    refreshCompleted();
  };

  const toggleNewTag = (tag) => {
    setNewTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  if (loading) return <div className="page-loading">Loading...</div>;
  if (error) return <div className="page-error">Error: {error}</div>;

  const activeItems = items || [];

  return (
    <div className="tasklist-page">
      <div className="tasklist-header">
        <div>
          <h1>Task List</h1>
          <p className="tasklist-subtitle">
            {activeItems.length} active · {completed.length} completed
          </p>
        </div>
        <button className="create-btn" onClick={() => setShowAddForm(!showAddForm)}>
          {showAddForm ? 'Cancel' : '+ New Task'}
        </button>
      </div>

      {/* Add form */}
      {showAddForm && (
        <div className="tl-add-form">
          <input
            className="tl-add-input"
            placeholder="What needs to get done?"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleCreate()}
            autoFocus
          />
          <textarea
            className="tl-add-textarea"
            placeholder="Description (optional)"
            value={newDescription}
            onChange={(e) => setNewDescription(e.target.value)}
            rows={2}
          />
          <div className="tl-add-tags">
            {allTags.map((tag) => (
              <button
                key={tag}
                className={`tl-tag-btn ${newTags.includes(tag) ? 'selected' : ''}`}
                onClick={() => toggleNewTag(tag)}
              >
                {tag}
              </button>
            ))}
          </div>
          <button className="add-btn" onClick={handleCreate}>Add Task</button>
        </div>
      )}

      {/* Active items */}
      <div className="tasklist-items">
        {activeItems.length === 0 && (
          <div className="empty-state">
            <p>Queue empty</p>
            <p className="text-muted">Everything's done, or nothing's started</p>
          </div>
        )}
        {activeItems.map((item) => (
          <TaskListCard
            key={item.id}
            item={item}
            onComplete={handleComplete}
            onDelete={handleDelete}
            onEdit={handleEdit}
            allTags={allTags}
          />
        ))}
      </div>

      {/* Completed section */}
      {completed.length > 0 && (
        <div className="completed-section">
          <button
            className="completed-toggle"
            onClick={() => setShowCompleted(!showCompleted)}
          >
            {showCompleted ? '▾' : '▸'} Completed ({completed.length})
            {showCompleted && (
              <span
                className="clear-link"
                onClick={(e) => { e.stopPropagation(); handleClearCompleted(); }}
              >
                Clear all
              </span>
            )}
          </button>
          {showCompleted && (
            <div className="completed-list">
              {completed.map((item) => (
                <div key={item.id} className="completed-item">
                  <span className="completed-check">✓</span>
                  <span className="completed-title">{item.title}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
