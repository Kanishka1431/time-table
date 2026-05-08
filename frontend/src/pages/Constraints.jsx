import { useEffect, useState } from 'react';
import { Settings, Shield, Sparkles, ToggleLeft, ToggleRight } from 'lucide-react';
import { getConstraints, updateConstraint } from '../services/api';

export default function Constraints() {
  const [constraints, setConstraints] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getConstraints()
      .then(res => setConstraints(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  async function toggleConstraint(constraint) {
    try {
      const res = await updateConstraint(constraint.id, { is_active: !constraint.is_active });
      setConstraints(constraints.map(c => c.id === constraint.id ? res.data : c));
    } catch (err) {
      alert('Failed to update: ' + err.message);
    }
  }

  const hard = constraints.filter(c => c.constraint_type === 'hard');
  const soft = constraints.filter(c => c.constraint_type === 'soft');

  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Constraints</h1>
        <p className="text-slate-600 mt-1">Configure scheduling rules and constraints</p>
      </div>

      {loading ? (
        <div className="loading-overlay"><div className="loading-spinner" /><span>Loading...</span></div>
      ) : constraints.length === 0 ? (
        <div className="glass-card-flat p-8 text-center text-slate-500">
          No constraints found. Seed the database from the Dashboard.
        </div>
      ) : (
        <div className="space-y-6">
          {/* Hard Constraints */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Shield size={18} className="text-rose-400" />
              <h2 className="text-lg font-semibold text-slate-900">Hard Constraints</h2>
              <span className="badge badge-rose ml-2">Must Enforce</span>
            </div>
            <div className="space-y-3">
              {hard.map((c) => (
                <div key={c.id} className="glass-card-flat p-4 flex items-center gap-4">
                  <button onClick={() => toggleConstraint(c)} className="flex-shrink-0">
                    {c.is_active ? (
                      <ToggleRight size={28} className="text-emerald-400" />
                    ) : (
                      <ToggleLeft size={28} className="text-slate-600" />
                    )}
                  </button>
                  <div className="flex-1">
                    <h3 className={`font-medium text-sm ${c.is_active ? 'text-slate-900' : 'text-slate-500'}`}>
                      {c.name}
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5">{c.description}</p>
                  </div>
                  <span className={`badge ${c.is_active ? 'badge-green' : 'badge-rose'}`}>
                    {c.is_active ? 'Active' : 'Disabled'}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Soft Constraints */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Sparkles size={18} className="text-amber-400" />
              <h2 className="text-lg font-semibold text-slate-900">Soft Constraints</h2>
              <span className="badge badge-amber ml-2">Future Optimization</span>
            </div>
            <div className="space-y-3">
              {soft.map((c) => (
                <div key={c.id} className="glass-card-flat p-4 flex items-center gap-4 opacity-70">
                  <button onClick={() => toggleConstraint(c)} className="flex-shrink-0">
                    {c.is_active ? (
                      <ToggleRight size={28} className="text-emerald-400" />
                    ) : (
                      <ToggleLeft size={28} className="text-slate-600" />
                    )}
                  </button>
                  <div className="flex-1">
                    <h3 className={`font-medium text-sm ${c.is_active ? 'text-slate-900' : 'text-slate-500'}`}>
                      {c.name}
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5">{c.description}</p>
                  </div>
                  <span className={`badge ${c.is_active ? 'badge-green' : 'badge-amber'}`}>
                    {c.is_active ? 'Active' : 'Planned'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
