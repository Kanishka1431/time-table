import { useEffect, useState } from 'react';
import { BookOpen } from 'lucide-react';
import { getSubjects } from '../services/api';

const groupColors = {
  primary: { bg: 'rgba(16, 185, 129, 0.1)', text: '#34d399', label: 'Primary (1-5)' },
  higher: { bg: 'rgba(139, 92, 246, 0.1)', text: '#a78bfa', label: 'Higher (6-10)' },
};

export default function Subjects() {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSubjects()
      .then(res => setSubjects(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const primary = subjects.filter(s => s.class_group === 'primary');
  const higher = subjects.filter(s => s.class_group === 'higher');

  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Subjects</h1>
        <p className="text-slate-600 mt-1">{subjects.length} subjects configured</p>
      </div>

      {loading ? (
        <div className="loading-overlay"><div className="loading-spinner" /><span>Loading...</span></div>
      ) : subjects.length === 0 ? (
        <div className="glass-card-flat p-8 text-center text-slate-500">
          No subjects found. Seed the database from the Dashboard.
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[{ label: 'Primary Classes (1-5)', items: primary, group: 'primary' },
            { label: 'Higher Classes (6-10)', items: higher, group: 'higher' }
          ].map(({ label, items, group }) => (
            <div key={group} className="glass-card-flat overflow-hidden">
              <div className="px-5 py-4 border-b border-slate-200 flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center"
                  style={{ background: groupColors[group].bg }}>
                  <BookOpen size={16} style={{ color: groupColors[group].text }} />
                </div>
                <h3 className="text-slate-900 font-semibold">{label}</h3>
                <span className="ml-auto badge badge-primary">{items.length} subjects</span>
              </div>
              <div className="p-4 space-y-2">
                {items.map(subj => {
                  const totalPerWeek = subj.weekly_frequency;
                  const barWidth = (totalPerWeek / 8) * 100;
                  return (
                    <div key={subj.id} className="flex items-center gap-4 p-3 rounded-xl bg-surface-100/30 hover:bg-surface-100/50 transition-colors">
                      <div className="w-2 h-2 rounded-full" style={{ background: groupColors[group].text }} />
                      <span className="text-slate-900 font-medium text-sm flex-1">{subj.name}</span>
                      <span className="text-[10px] text-slate-500 font-mono">{subj.code}</span>
                      <div className="w-24 flex items-center gap-2">
                        <div className="flex-1 h-1.5 rounded-full bg-surface-800 overflow-hidden">
                          <div className="h-full rounded-full transition-all duration-500"
                            style={{ width: `${barWidth}%`, background: groupColors[group].text }} />
                        </div>
                        <span className="text-xs font-semibold text-slate-900">{totalPerWeek}/w</span>
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="px-5 py-3 border-t border-slate-200 text-xs text-slate-500">
                Total weekly periods: {items.reduce((a, s) => a + s.weekly_frequency, 0)} / 48 slots
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
