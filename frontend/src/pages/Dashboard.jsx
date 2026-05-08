import { useEffect, useState } from 'react';
import {
  Users, BookOpen, School, Calendar, Wand2, AlertTriangle,
  ArrowRight, Database, CheckCircle2, XCircle
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getTeachers, getSubjects, getClasses, getSchedules, seedDatabase, healthCheck } from '../services/api';

export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    teachers: 0, subjects: 0, classes: 0, schedules: 0
  });
  const [loading, setLoading] = useState(true);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [seeding, setSeeding] = useState(false);
  const [seedResult, setSeedResult] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      await healthCheck();
      setBackendStatus('connected');
      const [t, s, c, sc] = await Promise.all([
        getTeachers(), getSubjects(), getClasses(), getSchedules()
      ]);
      setStats({
        teachers: t.data.length,
        subjects: s.data.length,
        classes: c.data.length,
        schedules: sc.data.length,
      });
    } catch (err) {
      setBackendStatus('error');
    } finally {
      setLoading(false);
    }
  }

  async function handleSeed() {
    setSeeding(true);
    setSeedResult(null);
    try {
      const res = await seedDatabase();
      setSeedResult(res.data);
      await loadData();
    } catch (err) {
      setSeedResult({ error: err.message });
    } finally {
      setSeeding(false);
    }
  }

  const statCards = [
    { label: 'Teachers', value: stats.teachers, icon: Users, color: '#6366f1', bg: 'rgba(99, 102, 241, 0.1)', path: '/teachers' },
    { label: 'Subjects', value: stats.subjects, icon: BookOpen, color: '#10b981', bg: 'rgba(16, 185, 129, 0.1)', path: '/subjects' },
    { label: 'Sections', value: stats.classes, icon: School, color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)', path: '/classes' },
    { label: 'Schedules', value: stats.schedules, icon: Calendar, color: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.1)', path: '/timetable' },
  ];

  return (
    <div className="animate-fade-in space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Dashboard</h1>
        <p className="text-slate-600 mt-1">AI Constraint-Based School Timetable Generation System</p>
      </div>

      {/* Backend Status */}
      <div className="glass-card-flat p-4 flex items-center gap-3">
        {backendStatus === 'connected' ? (
          <>
            <CheckCircle2 size={18} className="text-emerald-400" />
            <span className="text-sm text-emerald-300 font-medium">Backend Connected</span>
          </>
        ) : backendStatus === 'error' ? (
          <>
            <XCircle size={18} className="text-rose-400" />
            <span className="text-sm text-rose-300 font-medium">Backend Offline — Start the FastAPI server</span>
          </>
        ) : (
          <>
            <div className="loading-spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
            <span className="text-sm text-slate-600">Connecting...</span>
          </>
        )}
      </div>

      {/* Stats Grid */}
      {loading ? (
        <div className="loading-overlay"><div className="loading-spinner" /><span>Loading stats...</span></div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {statCards.map((card, i) => (
            <div
              key={card.label}
              className="stat-card cursor-pointer group"
              onClick={() => navigate(card.path)}
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                  style={{ background: card.bg }}>
                  <card.icon size={20} style={{ color: card.color }} />
                </div>
                <ArrowRight size={16} className="text-slate-600 group-hover:text-slate-600 transition-colors" />
              </div>
              <p className="text-3xl font-bold text-slate-900">{card.value}</p>
              <p className="text-sm text-slate-600 mt-1">{card.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Seed Data */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-3">
            <Database size={20} className="text-primary-400" />
            <h3 className="text-lg font-semibold text-slate-900">Seed Database</h3>
          </div>
          <p className="text-sm text-slate-600 mb-4">
            Populate the database with sample school data: 50 sections, 14 subjects, ~60 teachers, and constraint rules.
          </p>
          <button onClick={handleSeed} disabled={seeding} className="btn-primary">
            {seeding ? (
              <><div className="loading-spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> Seeding...</>
            ) : (
              <><Database size={16} /> Seed Now</>
            )}
          </button>
          {seedResult && (
            <div className="mt-3 p-3 rounded-lg bg-surface-100/50 text-xs text-slate-700">
              {seedResult.error ? (
                <span className="text-rose-400">{seedResult.error}</span>
              ) : (
                <pre>{JSON.stringify(seedResult.summary, null, 2)}</pre>
              )}
            </div>
          )}
        </div>

        {/* Generate Timetable */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-3">
            <Wand2 size={20} className="text-violet-400" />
            <h3 className="text-lg font-semibold text-slate-900">Generate Timetable</h3>
          </div>
          <p className="text-sm text-slate-600 mb-4">
            Run the greedy constraint-based scheduler to generate a conflict-free timetable for all 50 sections.
          </p>
          <button onClick={() => navigate('/generate')} className="btn-primary"
            style={{ background: 'linear-gradient(135deg, #8b5cf6, #6d28d9)' }}>
            <Wand2 size={16} /> Go to Generator
          </button>
        </div>
      </div>

      {/* School Config Summary */}
      <div className="glass-card-flat p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">School Configuration</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div><span className="text-slate-500">Classes:</span> <span className="text-slate-900 font-medium">1 - 10</span></div>
          <div><span className="text-slate-500">Sections:</span> <span className="text-slate-900 font-medium">A, B, C, D, E</span></div>
          <div><span className="text-slate-500">Days:</span> <span className="text-slate-900 font-medium">Mon - Sat</span></div>
          <div><span className="text-slate-500">Periods/Day:</span> <span className="text-slate-900 font-medium">8</span></div>
          <div><span className="text-slate-500">Timing:</span> <span className="text-slate-900 font-medium">8:30 AM - 3:00 PM</span></div>
          <div><span className="text-slate-500">Total Sections:</span> <span className="text-slate-900 font-medium">50</span></div>
          <div><span className="text-slate-500">Max Periods/Day:</span> <span className="text-slate-900 font-medium">6 per teacher</span></div>
          <div><span className="text-slate-500">Max Periods/Week:</span> <span className="text-slate-900 font-medium">32 per teacher</span></div>
        </div>
      </div>
    </div>
  );
}
