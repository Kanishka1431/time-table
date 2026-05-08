import { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, Calendar, ChevronDown } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import { getSchedules, getConflicts } from '../services/api';

export default function ConflictViewer() {
  const [searchParams] = useSearchParams();
  const [schedules, setSchedules] = useState([]);
  const [selectedSchedule, setSelectedSchedule] = useState(null);
  const [loading, setLoading] = useState(true);
  const [conflicts, setConflicts] = useState(null);
  const [conflictLoading, setConflictLoading] = useState(false);

  useEffect(() => {
    getSchedules()
      .then(res => {
        setSchedules(res.data);
        const paramId = searchParams.get('schedule');
        if (paramId && res.data.length > 0) {
          const found = res.data.find(s => s.id === parseInt(paramId));
          setSelectedSchedule(found || res.data[0]);
        } else if (res.data.length > 0) {
          setSelectedSchedule(res.data[0]);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (selectedSchedule) loadConflicts();
  }, [selectedSchedule]);

  async function loadConflicts() {
    setConflictLoading(true);
    try {
      const res = await getConflicts(selectedSchedule.id);
      setConflicts(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setConflictLoading(false);
    }
  }

  const report = conflicts?.conflict_report;
  const hasConflicts = report && report.total_conflicts > 0;

  const sections = [
    {
      title: 'Unsatisfied Subject Frequencies',
      items: report?.unsatisfied_frequencies || [],
      icon: '📚',
      color: 'amber',
      desc: 'Subjects that could not be scheduled for the required number of weekly periods.',
    },
    {
      title: 'Overloaded Teachers',
      items: report?.overloaded_teachers || [],
      icon: '👩‍🏫',
      color: 'rose',
      desc: 'Teachers exceeding their maximum period limits.',
    },
    {
      title: 'Teacher Clashes',
      items: report?.teacher_clashes || [],
      icon: '⚡',
      color: 'rose',
      desc: 'Same teacher assigned to multiple sections at the same time.',
    },
    {
      title: 'Section Clashes',
      items: report?.section_clashes || [],
      icon: '🔀',
      color: 'rose',
      desc: 'Same section assigned multiple subjects at the same time.',
    },
    {
      title: 'Unavailable Slots',
      items: report?.unavailable_slots || [],
      icon: '🚫',
      color: 'amber',
      desc: 'Slots that could not be assigned due to constraint violations.',
    },
  ];

  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Conflict Viewer</h1>
        <p className="text-slate-600 mt-1">Analyze scheduling conflicts and constraint violations</p>
      </div>

      {loading ? (
        <div className="loading-overlay"><div className="loading-spinner" /><span>Loading...</span></div>
      ) : schedules.length === 0 ? (
        <div className="glass-card-flat p-8 text-center text-slate-500">
          No schedules generated yet.
        </div>
      ) : (
        <>
          {/* Schedule Selector */}
          <div className="glass-card-flat p-4 flex items-center gap-4">
            <Calendar size={16} className="text-primary-400" />
            <select
              value={selectedSchedule?.id || ''}
              onChange={(e) => {
                const s = schedules.find(s => s.id === parseInt(e.target.value));
                setSelectedSchedule(s);
              }}
              className="form-select"
              style={{ width: 'auto', minWidth: 250 }}
            >
              {schedules.map(s => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.status})
                </option>
              ))}
            </select>
          </div>

          {conflictLoading ? (
            <div className="loading-overlay"><div className="loading-spinner" /><span>Loading conflicts...</span></div>
          ) : !report ? (
            <div className="glass-card-flat p-8 text-center text-slate-500">No conflict data available.</div>
          ) : !hasConflicts ? (
            <div className="glass-card p-8 text-center" style={{ borderColor: 'rgba(16, 185, 129, 0.2)' }}>
              <CheckCircle2 size={48} className="text-emerald-400 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-emerald-300 mb-2">No Conflicts!</h2>
              <p className="text-sm text-slate-600">
                The timetable was generated without any constraint violations. All hard constraints are satisfied.
              </p>
            </div>
          ) : (
            <>
              {/* Summary */}
              <div className="glass-card-flat p-5 flex items-center gap-4"
                style={{ borderColor: 'rgba(245, 158, 11, 0.2)' }}>
                <AlertTriangle size={24} className="text-amber-400 flex-shrink-0" />
                <div>
                  <h3 className="text-slate-900 font-semibold">
                    {report.total_conflicts} conflict{report.total_conflicts > 1 ? 's' : ''} detected
                  </h3>
                  <p className="text-sm text-slate-600">
                    Review the issues below and consider adjusting teacher mappings or adding more teachers.
                  </p>
                </div>
              </div>

              {/* Conflict Sections */}
              <div className="space-y-4">
                {sections.map((sec) => {
                  if (sec.items.length === 0) return null;
                  return (
                    <div key={sec.title} className="glass-card-flat overflow-hidden">
                      <div className={`px-5 py-4 border-b border-slate-200 flex items-center gap-3`}>
                        <span className="text-lg">{sec.icon}</span>
                        <h3 className="text-slate-900 font-semibold text-sm">{sec.title}</h3>
                        <span className={`badge badge-${sec.color} ml-auto`}>{sec.items.length}</span>
                      </div>
                      <p className="px-5 py-2 text-xs text-slate-500">{sec.desc}</p>
                      <div className="p-4 space-y-2">
                        {sec.items.map((item, i) => (
                          <div key={i} className="p-3 rounded-xl bg-surface-100/30 text-sm">
                            <p className="text-slate-700">{item.description}</p>
                            {item.remaining !== undefined && (
                              <p className="text-xs text-amber-400 mt-1">
                                {item.remaining} period{item.remaining > 1 ? 's' : ''} still needed
                              </p>
                            )}
                            {item.weekly_count !== undefined && (
                              <p className="text-xs text-rose-400 mt-1">
                                {item.weekly_count} / {item.max_per_week} periods assigned
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Generation Stats */}
              {conflicts?.generation_log && (
                <div className="glass-card-flat p-5">
                  <h3 className="text-sm font-semibold text-slate-700 mb-3">Generation Statistics</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                    {Object.entries(conflicts.generation_log).map(([key, value]) => (
                      <div key={key} className="flex justify-between p-2 rounded-lg bg-surface-100/30">
                        <span className="text-slate-500">{key.replace(/_/g, ' ')}</span>
                        <span className="text-slate-900 font-medium">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}
