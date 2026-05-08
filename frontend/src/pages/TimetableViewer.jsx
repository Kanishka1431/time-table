import { useEffect, useState } from 'react';
import { Calendar, Eye, Users, ChevronDown, Trash2, Printer } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import {
  getSchedules, getClassTimetable, getTeacherTimetable,
  getTeachers, deleteSchedule
} from '../services/api';
import TimetableGrid from '../components/TimetableGrid';

export default function TimetableViewer() {
  const [searchParams] = useSearchParams();
  const [schedules, setSchedules] = useState([]);
  const [selectedSchedule, setSelectedSchedule] = useState(null);
  const [viewMode, setViewMode] = useState('class'); // class or teacher
  const [loading, setLoading] = useState(true);
  const [gridLoading, setGridLoading] = useState(false);
  const [grid, setGrid] = useState(null);
  const [teachers, setTeachers] = useState([]);
  const [teacherInfo, setTeacherInfo] = useState(null);

  // Class/Teacher selection
  const [classNum, setClassNum] = useState(1);
  const [section, setSection] = useState('A');
  const [teacherId, setTeacherId] = useState(null);

  useEffect(() => {
    Promise.all([getSchedules(), getTeachers()])
      .then(([sRes, tRes]) => {
        setSchedules(sRes.data);
        setTeachers(tRes.data);
        const paramId = searchParams.get('schedule');
        if (paramId && sRes.data.length > 0) {
          const found = sRes.data.find(s => s.id === parseInt(paramId));
          setSelectedSchedule(found || sRes.data[0]);
        } else if (sRes.data.length > 0) {
          setSelectedSchedule(sRes.data[0]);
        }
        if (tRes.data.length > 0) setTeacherId(tRes.data[0].id);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (selectedSchedule) loadGrid();
  }, [selectedSchedule, viewMode, classNum, section, teacherId]);

  async function loadGrid() {
    if (!selectedSchedule) return;
    setGridLoading(true);
    setGrid(null);
    setTeacherInfo(null);
    try {
      if (viewMode === 'class') {
        const res = await getClassTimetable(selectedSchedule.id, classNum, section);
        setGrid(res.data.grid);
      } else {
        if (!teacherId) return;
        const res = await getTeacherTimetable(selectedSchedule.id, teacherId);
        setGrid(res.data.grid);
        setTeacherInfo(res.data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setGridLoading(false);
    }
  }

  async function handleDeleteSchedule(id) {
    if (!confirm('Delete this schedule and all its data?')) return;
    try {
      await deleteSchedule(id);
      setSchedules(schedules.filter(s => s.id !== id));
      if (selectedSchedule?.id === id) {
        setSelectedSchedule(schedules.filter(s => s.id !== id)[0] || null);
      }
    } catch (err) {
      alert('Failed: ' + err.message);
    }
  }

  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Timetable Viewer</h1>
        <p className="text-slate-600 mt-1">View generated timetables by class or teacher</p>
      </div>

      {loading ? (
        <div className="loading-overlay"><div className="loading-spinner" /><span>Loading...</span></div>
      ) : schedules.length === 0 ? (
        <div className="glass-card-flat p-8 text-center text-slate-500">
          No schedules generated yet. Go to the Generator page to create one.
        </div>
      ) : (
        <>
          {/* Controls Row */}
          <div className="glass-card-flat p-4 flex flex-wrap items-center gap-4">
            {/* Schedule Selector */}
            <div className="flex items-center gap-2">
              <Calendar size={16} className="text-primary-400" />
              <select
                value={selectedSchedule?.id || ''}
                onChange={(e) => {
                  const s = schedules.find(s => s.id === parseInt(e.target.value));
                  setSelectedSchedule(s);
                }}
                className="form-select"
                style={{ width: 'auto', minWidth: 200 }}
              >
                {schedules.map(s => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.status})
                  </option>
                ))}
              </select>
            </div>

            {/* View Mode Toggle */}
            <div className="flex rounded-xl overflow-hidden border border-slate-300">
              <button
                onClick={() => setViewMode('class')}
                className={`px-4 py-2 text-sm font-medium flex items-center gap-2 transition-colors ${
                  viewMode === 'class' ? 'bg-primary-600/20 text-primary-300' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Eye size={14} /> Class View
              </button>
              <button
                onClick={() => setViewMode('teacher')}
                className={`px-4 py-2 text-sm font-medium flex items-center gap-2 transition-colors ${
                  viewMode === 'teacher' ? 'bg-primary-600/20 text-primary-300' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Users size={14} /> Teacher View
              </button>
            </div>

            {/* Class/Teacher Selector */}
            {viewMode === 'class' ? (
              <div className="flex items-center gap-2">
                <select value={classNum} onChange={(e) => setClassNum(parseInt(e.target.value))}
                  className="form-select" style={{ width: 'auto' }}>
                  {[1,2,3,4,5,6,7,8,9,10].map(n => (
                    <option key={n} value={n}>Class {n}</option>
                  ))}
                </select>
                <select value={section} onChange={(e) => setSection(e.target.value)}
                  className="form-select" style={{ width: 'auto' }}>
                  {['A','B','C','D','E'].map(s => (
                    <option key={s} value={s}>Section {s}</option>
                  ))}
                </select>
              </div>
            ) : (
              <select
                value={teacherId || ''}
                onChange={(e) => setTeacherId(parseInt(e.target.value))}
                className="form-select" style={{ width: 'auto', minWidth: 200 }}
              >
                {teachers.map(t => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            )}

            {/* Print */}
            {selectedSchedule && grid && (
              <button
                onClick={() => window.print()}
                className="ml-auto flex items-center gap-2 btn-secondary print-hidden"
                title="Print Timetable"
              >
                <Printer size={16} /> Print
              </button>
            )}

            {/* Delete */}
            {selectedSchedule && (
              <button
                onClick={() => handleDeleteSchedule(selectedSchedule.id)}
                className={grid ? "text-slate-500 hover:text-rose-400 transition-colors print-hidden" : "ml-auto text-slate-500 hover:text-rose-400 transition-colors print-hidden"}
                title="Delete schedule"
              >
                <Trash2 size={16} />
              </button>
            )}
          </div>

          {/* Teacher Info Bar */}
          {viewMode === 'teacher' && teacherInfo && (
            <div className="glass-card-flat p-4 flex flex-wrap items-center gap-6 text-sm">
              <span className="text-slate-900 font-semibold">{teacherInfo.teacher_name}</span>
              <span className="badge badge-primary">
                {teacherInfo.weekly_periods} / {teacherInfo.max_per_week} periods/week
              </span>
              {Object.entries(teacherInfo.daily_load || {}).map(([day, count]) => (
                <span key={day} className="text-xs text-slate-600">
                  {day.slice(0,3)}: <span className={count > teacherInfo.max_per_day ? 'text-rose-400 font-bold' : 'text-slate-900'}>{count}</span>
                </span>
              ))}
            </div>
          )}

          {/* Timetable Grid */}
          <div className="glass-card-flat p-4">
            <div className="mb-3 flex items-center gap-2">
              <h3 className="text-sm font-semibold text-slate-700">
                {viewMode === 'class' ? `Class ${classNum} - Section ${section}` : teacherInfo?.teacher_name || 'Select a teacher'}
              </h3>
              {selectedSchedule && (
                <span className={`badge ml-2 ${selectedSchedule.status === 'active' ? 'badge-green' : 'badge-amber'}`}>
                  {selectedSchedule.status}
                </span>
              )}
            </div>
            {gridLoading ? (
              <div className="loading-overlay"><div className="loading-spinner" /><span>Loading timetable...</span></div>
            ) : (
              <TimetableGrid grid={grid} mode={viewMode} />
            )}
          </div>

          {/* Legend */}
          <div className="glass-card-flat p-4">
            <h4 className="text-xs font-semibold text-slate-500 mb-3 uppercase tracking-wider">Subject Color Legend</h4>
            <div className="flex flex-wrap gap-3">
              {[
                { name: 'English', cls: 'subject-english' },
                { name: 'Math', cls: 'subject-math' },
                { name: 'Science/EVS', cls: 'subject-science' },
                { name: 'Social/GK', cls: 'subject-social' },
                { name: 'Computer', cls: 'subject-computer' },
                { name: 'PT', cls: 'subject-pt' },
                { name: 'Language', cls: 'subject-language' },
                { name: 'Free', cls: 'timetable-cell-free' },
                { name: 'Break', cls: 'timetable-cell-break' },
              ].map(item => (
                <div key={item.name} className={`${item.cls} timetable-cell px-3 py-1.5 text-xs font-medium`}>
                  {item.name}
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
