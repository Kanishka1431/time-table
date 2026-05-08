import { useEffect, useState } from 'react';
import { School } from 'lucide-react';
import { getClassesGrouped } from '../services/api';

const sectionColors = ['#6366f1', '#10b981', '#f59e0b', '#f43f5e', '#06b6d4'];

export default function Classes() {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getClassesGrouped()
      .then(res => setGroups(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Classes & Sections</h1>
        <p className="text-slate-600 mt-1">10 classes × 5 sections = 50 total sections</p>
      </div>

      {loading ? (
        <div className="loading-overlay"><div className="loading-spinner" /><span>Loading...</span></div>
      ) : groups.length === 0 ? (
        <div className="glass-card-flat p-8 text-center text-slate-500">
          No classes found. Seed the database from the Dashboard.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {groups.map((group) => (
            <div key={group.class_number} className="glass-card p-5">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center text-lg font-bold"
                  style={{
                    background: group.class_group === 'primary' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(139, 92, 246, 0.15)',
                    color: group.class_group === 'primary' ? '#34d399' : '#a78bfa',
                  }}>
                  {group.class_number}
                </div>
                <div>
                  <h3 className="text-slate-900 font-semibold text-sm">Class {group.class_number}</h3>
                  <span className={`text-[10px] font-medium ${group.class_group === 'primary' ? 'text-emerald-400' : 'text-violet-400'}`}>
                    {group.class_group === 'primary' ? 'Primary' : 'Higher'}
                  </span>
                </div>
              </div>
              <div className="flex gap-2 flex-wrap">
                {group.sections.map((sec, i) => (
                  <div
                    key={sec.id}
                    className="w-9 h-9 rounded-lg flex items-center justify-center text-xs font-bold transition-transform hover:scale-110"
                    style={{
                      background: `${sectionColors[i]}20`,
                      color: sectionColors[i],
                      border: `1px solid ${sectionColors[i]}30`,
                    }}
                  >
                    {sec.section}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
