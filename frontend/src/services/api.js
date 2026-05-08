import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

// ─── Teachers ───
export const getTeachers = () => api.get('/teachers');
export const createTeacher = (data) => api.post('/teachers', data);
export const updateTeacher = (id, data) => api.put(`/teachers/${id}`, data);
export const deleteTeacher = (id) => api.delete(`/teachers/${id}`);
export const getTeacherMappings = (id) => api.get(`/teachers/${id}/mappings`);
export const getAllMappings = () => api.get('/teachers/mappings/all');
export const createMapping = (data) => api.post('/teachers/mappings', data);

// ─── Subjects ───
export const getSubjects = () => api.get('/subjects');
export const createSubject = (data) => api.post('/subjects', data);
export const updateSubject = (id, data) => api.put(`/subjects/${id}`, data);

// ─── Classes ───
export const getClasses = () => api.get('/classes');
export const getClassesGrouped = () => api.get('/classes/grouped');

// ─── Constraints ───
export const getConstraints = () => api.get('/constraints');
export const updateConstraint = (id, data) => api.put(`/constraints/${id}`, data);

// ─── Timetable ───
export const generateTimetable = (data = {}) => api.post('/timetable/generate', data);
export const getSchedules = () => api.get('/timetable/schedules');
export const getScheduleDetail = (id) => api.get(`/timetable/schedules/${id}`);
export const deleteSchedule = (id) => api.delete(`/timetable/schedules/${id}`);
export const getClassTimetable = (scheduleId, classNum, section) =>
  api.get(`/timetable/class-view/${scheduleId}/${classNum}/${section}`);
export const getTeacherTimetable = (scheduleId, teacherId) =>
  api.get(`/timetable/teacher-view/${scheduleId}/${teacherId}`);
export const getConflicts = (scheduleId) => api.get(`/timetable/conflicts/${scheduleId}`);

// ─── Seed & Config ───
export const seedDatabase = () => api.post('/seed');
export const getConfig = () => api.get('/config');
export const healthCheck = () => api.get('/health');

export default api;
