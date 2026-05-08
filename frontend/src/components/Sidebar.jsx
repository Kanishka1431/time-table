import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Users, BookOpen, School, Settings,
  Wand2, Calendar, AlertTriangle, ChevronLeft, ChevronRight, Zap
} from 'lucide-react';
import { useState } from 'react';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/teachers', icon: Users, label: 'Teachers' },
  { path: '/subjects', icon: BookOpen, label: 'Subjects' },
  { path: '/classes', icon: School, label: 'Classes' },
  { path: '/constraints', icon: Settings, label: 'Constraints' },
  { path: '/generate', icon: Wand2, label: 'Generator' },
  { path: '/timetable', icon: Calendar, label: 'Timetable' },
  { path: '/conflicts', icon: AlertTriangle, label: 'Conflicts' },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`fixed left-0 top-0 h-screen z-50 flex flex-col transition-all duration-300 ease-in-out ${
        collapsed ? 'w-[72px]' : 'w-[240px]'
      }`}
      style={{
        background: 'linear-gradient(180deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.98) 100%)',
        borderRight: '1px solid rgba(148, 163, 184, 0.2)',
        backdropFilter: 'blur(20px)',
      }}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 h-16 border-b border-slate-200">
        <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}>
          <Zap size={18} className="text-slate-900" />
        </div>
        {!collapsed && (
          <div className="animate-fade-in">
            <h1 className="text-sm font-bold text-slate-800 tracking-tight">ScheduleAI</h1>
            <p className="text-[10px] text-slate-500 font-medium">Timetable System</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group ${
                isActive
                  ? 'bg-primary-50 text-primary-600'
                  : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <item.icon
                  size={18}
                  className={`flex-shrink-0 transition-colors ${
                    isActive ? 'text-primary-500' : 'text-slate-600 group-hover:text-slate-500'
                  }`}
                />
                {!collapsed && (
                  <span className="animate-fade-in">{item.label}</span>
                )}
                {isActive && !collapsed && (
                  <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary-400" />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Collapse Toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-center h-12 border-t border-slate-200 text-slate-600 hover:text-slate-600 transition-colors"
      >
        {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>
    </aside>
  );
}
