import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Teachers from './pages/Teachers';
import Subjects from './pages/Subjects';
import Classes from './pages/Classes';
import Constraints from './pages/Constraints';
import Generator from './pages/Generator';
import TimetableViewer from './pages/TimetableViewer';
import ConflictViewer from './pages/ConflictViewer';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/teachers" element={<Teachers />} />
          <Route path="/subjects" element={<Subjects />} />
          <Route path="/classes" element={<Classes />} />
          <Route path="/constraints" element={<Constraints />} />
          <Route path="/generate" element={<Generator />} />
          <Route path="/timetable" element={<TimetableViewer />} />
          <Route path="/conflicts" element={<ConflictViewer />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
