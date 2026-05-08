import { useEffect, useState } from 'react';
import { Users, Search, Plus, Edit2, Trash2, BookOpen } from 'lucide-react';
import { getTeachers, deleteTeacher, getTeacherMappings } from '../services/api';

export default function Teachers() {
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState(null);
  const [mappings, setMappings] = useState([]);

  useEffect(() => { loadTeachers(); }, []);

  async function loadTeachers() {
    try {
      const res = await getTeachers();
      setTeachers(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id) {
    if (!confirm('Delete this teacher?')) return;
    try {
      await deleteTeacher(id);
      setTeachers(teachers.filter(t => t.id !== id));
      if (selected?.id === id) setSelected(null);
    } catch (err) {
      alert('Failed to delete: ' + err.message);
    }
  }

  async function handleSelect(teacher) {
    setSelected(teacher);
    try {
      const res = await getTeacherMappings(teacher.id);
      setMappings(res.data);
    } catch {
      setMappings([]);
    }
  }

  const filtered = teachers.filter(t =>
    t.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Teachers</h1>
          <p className="text-slate-600 mt-1">{teachers.length} teachers registered</p>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
        <input
          type="text"
          placeholder="Search teachers..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="form-input pl-10"
          style={{ maxWidth: 400 }}
        />
      </div>

      <div className="flex gap-6">
        {/* Table */}
        <div className="flex-1 glass-card-flat overflow-hidden">
          {loading ? (
            <div className="loading-overlay"><div className="loading-spinner" /><span>Loading...</span></div>
          ) : (
            <div className="overflow-x-auto">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Max/Day</th>
                    <th>Max/Week</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((teacher) => (
                    <tr
                      key={teacher.id}
                      className={`cursor-pointer ${selected?.id === teacher.id ? 'bg-primary-600/10' : ''}`}
                      onClick={() => handleSelect(teacher)}
                    >
                      <td>
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold"
                            style={{ background: 'rgba(99, 102, 241, 0.15)', color: '#a5b4fc' }}>
                            {teacher.name.charAt(0)}
                          </div>
                          <span className="font-medium text-slate-900">{teacher.name}</span>
                        </div>
                      </td>
                      <td className="text-slate-600 text-xs">{teacher.email || '—'}</td>
                      <td><span className="badge badge-primary">{teacher.max_periods_per_day}</span></td>
                      <td><span className="badge badge-violet">{teacher.max_periods_per_week}</span></td>
                      <td>
                        <span className={`badge ${teacher.is_active ? 'badge-green' : 'badge-rose'}`}>
                          {teacher.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td>
                        <button
                          onClick={(e) => { e.stopPropagation(); handleDelete(teacher.id); }}
                          className="text-slate-500 hover:text-rose-400 transition-colors"
                        >
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                  {filtered.length === 0 && (
                    <tr><td colSpan={6} className="text-center py-8 text-slate-500">
                      {search ? 'No matching teachers' : 'No teachers found. Seed the database first.'}
                    </td></tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Detail Panel */}
        {selected && (
          <div className="w-[320px] glass-card p-5 animate-slide-in flex-shrink-0">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold"
                style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: 'white' }}>
                {selected.name.charAt(0)}
              </div>
              <div>
                <h3 className="text-slate-900 font-semibold">{selected.name}</h3>
                <p className="text-xs text-slate-600">{selected.email || 'No email'}</p>
              </div>
            </div>

            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-600">Max Periods/Day</span>
                <span className="text-slate-900 font-medium">{selected.max_periods_per_day}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Max Periods/Week</span>
                <span className="text-slate-900 font-medium">{selected.max_periods_per_week}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Status</span>
                <span className={selected.is_active ? 'text-emerald-400' : 'text-rose-400'}>
                  {selected.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>

            {/* Mappings */}
            <div className="mt-5 pt-4 border-t border-slate-200">
              <h4 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
                <BookOpen size={14} /> Subject Mappings
              </h4>
              {mappings.length > 0 ? (
                <div className="space-y-2">
                  {mappings.map((m) => (
                    <div key={m.id} className="flex items-center justify-between p-2 rounded-lg bg-surface-100/50 text-xs">
                      <span className="text-slate-900 font-medium">{m.subject_name}</span>
                      <span className="badge badge-cyan">Class {m.class_range_start}-{m.class_range_end}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-500">No mappings found</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
