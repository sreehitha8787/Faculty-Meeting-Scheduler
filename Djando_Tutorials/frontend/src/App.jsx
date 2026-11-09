import './App.css';
import Login from './pages/Login';
import Home from './pages/Home';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MeetingSlots from './pages/MeetingSlots';
import Calendar from './pages/Calendar';
import ProtectedRoute from './components/ProtectedRoute';
import WeeklyTimetable from './pages/WeeklyTimetable';
import AcademicCalendar from './pages/AcademicCalendar';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/home" element={<ProtectedRoute><Home /></ProtectedRoute>} />
        <Route path="/home/timetable" element={<ProtectedRoute><WeeklyTimetable /></ProtectedRoute>} />
        <Route path="/home/meetingslots" element={<ProtectedRoute><MeetingSlots /></ProtectedRoute>} />
        <Route path="/home/calendar" element={<ProtectedRoute><Calendar /></ProtectedRoute>} />
        <Route path="/home/academic-calendar" element={<ProtectedRoute><AcademicCalendar /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/home" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
