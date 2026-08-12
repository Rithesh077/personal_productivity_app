import { useState } from 'react';
import './TaskListCard.css';

/**
 * Task list item card for the priority queue.
 * Shows title, description, tags, and completion actions.
 */
export default function TaskListCard({
  item,
  onComplete,
  onDelete,
  onEdit,
  allTags,
}) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(item.title);
  const [description, setDescription] = useState(item.description);
  const [selectedTags, setSelectedTags] = useState(item.tags);

  const handleSave = () => {
    onEdit(item.id, {
      title: title.trim() || item.title,
      description: description.trim(),
      tags: selectedTags,
    });
    setEditing(false);
  };

  const toggleTag = (tag) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  const tagColor = (tag) => {
    const colors = {
      learning: 'var(--tag-learning)',
      bug: 'var(--tag-bug)',
      admin: 'var(--tag-admin)',
      creative: 'var(--tag-creative)',
      health: 'var(--tag-health)',
      urgent: 'var(--tag-urgent)',
    };
    return colors[tag] || 'var(--teal)';
  };

  if (editing) {
    return (
      <div className="task-list-card editing">
        <input
          className="tl-edit-input"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Task title"
          autoFocus
        />
        <textarea
          className="tl-edit-textarea"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Description (optional)"
          rows={2}
        />
        <div className="tl-tags-edit">
          {(allTags || []).map((tag) => (
            <button
              key={tag}
              className={`tl-tag-btn ${selectedTags.includes(tag) ? 'selected' : ''}`}
              style={{ '--tag-color': tagColor(tag) }}
              onClick={() => toggleTag(tag)}
            >
              {tag}
            </button>
          ))}
        </div>
        <div className="tl-edit-actions">
          <button className="add-btn" onClick={handleSave}>Save</button>
          <button className="cancel-btn" onClick={() => setEditing(false)}>Cancel</button>
        </div>
      </div>
    );
  }

  return (
    <div className={`task-list-card ${item.is_completed ? 'completed' : ''}`}>
      <button className="tl-checkbox" onClick={() => onComplete(item.id)}>○</button>

      <div className="tl-content">
        <span className="tl-title">{item.title}</span>
        {item.description && <p className="tl-description">{item.description}</p>}
        {item.tags.length > 0 && (
          <div className="tl-tags">
            {item.tags.map((tag) => (
              <span key={tag} className="tl-tag" style={{ color: tagColor(tag), borderColor: tagColor(tag) }}>
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="tl-actions">
        <button className="icon-btn small" onClick={() => setEditing(true)} title="Edit">✎</button>
        <button className="icon-btn small danger" onClick={() => onDelete(item.id)} title="Delete">✕</button>
      </div>
    </div>
  );
}
