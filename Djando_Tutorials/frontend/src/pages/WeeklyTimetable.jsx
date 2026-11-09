import React, { useCallback, useEffect, useState } from 'react';
import { FiClock, FiRefreshCw, FiAlertCircle } from 'react-icons/fi';
import Layout from '../components/Layout';
import api from '../api';
import '../App.css';

const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
const formatTime = (value) => value ? String(value).slice(0, 5) : '—';

export default function WeeklyTimetable() {
  const [timetable, setTimetable] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const loadTimetable = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await api.get('/get_timetable/');
      setTimetable(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      setError(err.response?.data?.detail || err.response?.data?.error || 'Could not load your weekly timetable.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { loadTimetable(); }, [loadTimetable]);

  return (
    <Layout>
      <div className="content-page weekly-timetable-page">
        <section className="page-intro">
          <div><div className="eyebrow">YOUR WORKSPACE</div><h1>Weekly timetable</h1><p>Your recurring class schedule, applied to every week including 2027.</p></div>
          <button className="button button-secondary" onClick={loadTimetable}><FiRefreshCw /> Refresh</button>
        </section>
        {error && <div className="alert alert-error" role="alert"><FiAlertCircle /><span>{error}</span></div>}
        <section className="weekly-timetable-grid">
          {days.map((day) => {
            const entries = timetable.filter((item) => item.day === day).sort((a, b) => (a.start_time || '').localeCompare(b.start_time || ''));
            return <article className="panel weekly-day-panel" key={day}>
              <div className="panel-heading"><div><span className="eyebrow">WEEKDAY</span><h2>{day}</h2></div><span className="schedule-count">{entries.length}</span></div>
              {isLoading ? <div className="loading-state"><span className="loading-spinner" /> Loading…</div> : entries.length ? <div className="schedule-list">{entries.map((item, index) => <div className="schedule-item" key={`${item.id || item.class_room}-${index}`}><div className="schedule-time"><strong>{formatTime(item.start_time)}</strong><span>{formatTime(item.end_time)}</span></div><div className="schedule-timeline"><span /></div><div className="schedule-details"><strong>{item.class_room || 'Scheduled class'}</strong><span>Recurring weekly slot</span></div></div>)}</div> : <div className="empty-state"><FiClock /><strong>No classes</strong></div>}
            </article>;
          })}
        </section>
      </div>
    </Layout>
  );
}
