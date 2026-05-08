import { useMemo } from 'react';

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const PERIODS = [1, 2, 3, 4, 5, 6, 7, 8];
const PERIOD_TIMES = {
  1: '8:30 - 9:15', 2: '9:15 - 10:00',
  3: '10:15 - 11:00', 4: '11:00 - 11:45',
  5: '12:30 - 1:15', 6: '1:15 - 2:00',
  7: '2:00 - 2:30', 8: '2:30 - 3:00',
};

function getSubjectClass(subjectName) {
  if (!subjectName) return 'timetable-cell-free';
  const lower = subjectName.toLowerCase();
  if (lower === 'free period') return 'timetable-cell-free';
  if (lower.includes('english')) return 'subject-english';
  if (lower.includes('math')) return 'subject-math';
  if (lower.includes('science') || lower.includes('evs')) return 'subject-science';
  if (lower.includes('social') || lower.includes('gk')) return 'subject-social';
  if (lower.includes('computer')) return 'subject-computer';
  if (lower.includes('pt')) return 'subject-pt';
  if (lower.includes('language')) return 'subject-language';
  return 'timetable-cell-free';
}

export default function TimetableGrid({ grid, mode = 'class' }) {
  // grid: { dayName: { period: { subject, teacher/class_info, slot_type } } }

  const rows = useMemo(() => {
    const result = [];

    // Insert break rows at correct positions
    const schedule = [
      { period: 1 }, { period: 2 },
      { type: 'short_break', label: 'Short Break (10:00 - 10:15)' },
      { period: 3 }, { period: 4 },
      { type: 'lunch_break', label: 'Lunch Break (11:45 - 12:30)' },
      { period: 5 }, { period: 6 }, { period: 7 }, { period: 8 },
    ];

    for (const item of schedule) {
      if (item.type) {
        result.push({ isBreak: true, label: item.label, type: item.type });
      } else {
        result.push({ isBreak: false, period: item.period });
      }
    }
    return result;
  }, []);

  if (!grid || Object.keys(grid).length === 0) {
    return (
      <div className="text-center py-12 text-slate-500">
        <p>No timetable data available</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse" style={{ minWidth: '800px' }}>
        <thead>
          <tr>
            <th className="timetable-cell timetable-cell-header" style={{ minWidth: '90px' }}>
              Period
            </th>
            {DAYS.map((day) => (
              <th key={day} className="timetable-cell timetable-cell-header">
                {day}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => {
            if (row.isBreak) {
              return (
                <tr key={`break-${idx}`}>
                  <td
                    colSpan={7}
                    className="timetable-cell timetable-cell-break text-center py-2"
                  >
                    ☕ {row.label}
                  </td>
                </tr>
              );
            }

            return (
              <tr key={`p-${row.period}`}>
                <td className="timetable-cell timetable-cell-period">
                  <span className="font-bold">P{row.period}</span>
                  <span className="text-[10px] opacity-60">{PERIOD_TIMES[row.period]}</span>
                </td>
                {DAYS.map((day) => {
                  const cell = grid?.[day]?.[row.period];
                  const subject = cell?.subject || 'Free Period';
                  const info = mode === 'class' ? cell?.teacher : cell?.class_info;
                  const isFree = !cell || cell.slot_type === 'free' || subject === 'Free Period';

                  return (
                    <td
                      key={day}
                      className={`timetable-cell ${isFree ? 'timetable-cell-free' : getSubjectClass(subject)}`}
                    >
                      <div className="font-semibold text-xs">{isFree ? '—' : subject}</div>
                      {info && !isFree && (
                        <div className="text-[10px] opacity-70 mt-0.5">{info}</div>
                      )}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
