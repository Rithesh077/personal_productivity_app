import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import Planner from './pages/Planner';
import TaskList from './pages/TaskList';
import Analytics from './pages/Analytics';
import './App.css';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <nav className="app-nav">
          <div className="nav-brand">Stride</div>
          <div className="nav-links">
            <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              <span className="nav-icon">◎</span>
              <span className="nav-label">Goals</span>
            </NavLink>
            <NavLink to="/tasks" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              <span className="nav-icon">☰</span>
              <span className="nav-label">Tasks</span>
            </NavLink>
            <NavLink to="/analytics" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              <span className="nav-icon">◆</span>
              <span className="nav-label">Analytics</span>
            </NavLink>
          </div>
        </nav>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<Planner />} />
            <Route path="/tasks" element={<TaskList />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
