import { useState } from 'react';
import { Wand2, CheckCircle2, XCircle, AlertTriangle, Clock, BarChart3 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { generateTimetable } from '../services/api';

export default function Generator() {
  const navigate = useNavigate();
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [name, setName] = useState('');

  async function handleGenerate() {
    setGenerating(true);
    setResult(null);
    try {
      const res = await generateTimetable({ name: name || undefined });
      setResult(res.data);
    } catch (err) {
      setResult({ error: err.response?.data?.detail || err.message });
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Timetable Generator</h1>
        <p className="text-slate-600 mt-1">Generate conflict-free timetables using constraint-based scheduling</p>
      </div>

      {/* Generator Card */}
      <div className="glass-card p-8 text-center">
        <div className="w-20 h-20 mx-auto rounded-2xl flex items-center justify-center mb-6"
          style={{
            background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(99, 102, 241, 0.2))',
            border: '1px solid rgba(139, 92, 246, 0.2)',
          }}>
          <Wand2 size={36} className="text-violet-400" />
        </div>
        <h2 className="text-xl font-bold text-slate-900 mb-2">Greedy Constraint-Based Scheduler</h2>
        <p className="text-sm text-slate-600 mb-6 max-w-lg mx-auto">
          The algorithm sorts subjects by scheduling difficulty, assigns harder subjects first,
          validates all hard constraints, and generates a fully valid timetable for all 50 sections.
        </p>

        <div className="max-w-sm mx-auto mb-6">
          <input
            type="text"
            placeholder="Schedule name (optional)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="form-input text-center"
          />
        </div>

        <button
          onClick={handleGenerate}
          disabled={generating}
          className="btn-primary text-lg px-8 py-3"
          style={{ background: generating ? undefined : 'linear-gradient(135deg, #8b5cf6, #6d28d9)' }}
        >
          {generating ? (
            <>
              <div className="loading-spinner" style={{ width: 20, height: 20, borderWidth: 2 }} />
              Generating... This may take a moment
            </>
          ) : (
            <><Wand2 size={20} /> Generate Timetable</>
          )}
        </button>

        {/* Algorithm Steps */}
        <div className="mt-8 flex flex-wrap justify-center gap-3 text-xs">
          {['Sort by difficulty', 'Assign subjects', 'Validate constraints', 'Balance workload', 'Fill free slots'].map((step, i) => (
            <div key={i} className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-800/50 text-slate-600">
              <span className="w-4 h-4 rounded-full bg-primary-600/20 text-primary-400 flex items-center justify-center text-[10px] font-bold">
                {i + 1}
              </span>
              {step}
            </div>
          ))}
        </div>
      </div>

      {/* Result */}
      {result && (
        <div className="animate-fade-in">
          {result.error ? (
            <div className="glass-card p-6 border-rose-500/20">
              <div className="flex items-center gap-3 text-rose-400 mb-3">
                <XCircle size={20} />
                <h3 className="font-semibold">Generation Failed</h3>
              </div>
              <p className="text-sm text-rose-300">{result.error}</p>
            </div>
          ) : (
            <div className="glass-card p-6" style={{ borderColor: result.success ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)' }}>
              <div className="flex items-center gap-3 mb-4">
                {result.success ? (
                  <><CheckCircle2 size={22} className="text-emerald-400" /><h3 className="text-lg font-semibold text-emerald-300">Timetable Generated Successfully!</h3></>
                ) : (
                  <><AlertTriangle size={22} className="text-amber-400" /><h3 className="text-lg font-semibold text-amber-300">Generated with Conflicts</h3></>
                )}
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                {[
                  { label: 'Sections', value: result.stats?.total_sections, icon: '📚' },
                  { label: 'Subjects Assigned', value: result.stats?.total_subjects_assigned, icon: '✅' },
                  { label: 'Free Periods', value: result.stats?.total_free_periods, icon: '📋' },
                  { label: 'Conflicts', value: result.stats?.total_conflicts, icon: result.stats?.total_conflicts > 0 ? '⚠️' : '🎉' },
                ].map((s) => (
                  <div key={s.label} className="p-3 rounded-xl bg-surface-100/50 text-center">
                    <div className="text-lg mb-1">{s.icon}</div>
                    <div className="text-xl font-bold text-slate-900">{s.value ?? '—'}</div>
                    <div className="text-[10px] text-slate-500">{s.label}</div>
                  </div>
                ))}
              </div>

              {/* Conflict Summary */}
              {result.conflict_report && result.conflict_report.total_conflicts > 0 && (
                <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/10 mb-4">
                  <h4 className="text-sm font-semibold text-amber-300 mb-2 flex items-center gap-2">
                    <AlertTriangle size={14} /> Conflict Summary
                  </h4>
                  <div className="text-xs text-slate-600 space-y-1">
                    {result.conflict_report.unsatisfied_frequencies?.length > 0 && (
                      <p>• {result.conflict_report.unsatisfied_frequencies.length} unsatisfied subject frequencies</p>
                    )}
                    {result.conflict_report.overloaded_teachers?.length > 0 && (
                      <p>• {result.conflict_report.overloaded_teachers.length} overloaded teachers</p>
                    )}
                    {result.conflict_report.teacher_clashes?.length > 0 && (
                      <p>• {result.conflict_report.teacher_clashes.length} teacher clashes</p>
                    )}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3 flex-wrap">
                <button
                  onClick={() => navigate(`/timetable?schedule=${result.schedule_id}`)}
                  className="btn-primary"
                >
                  <BarChart3 size={16} /> View Timetable
                </button>
                {result.conflict_report?.total_conflicts > 0 && (
                  <button
                    onClick={() => navigate(`/conflicts?schedule=${result.schedule_id}`)}
                    className="btn-secondary"
                  >
                    <AlertTriangle size={16} /> View Conflicts
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
