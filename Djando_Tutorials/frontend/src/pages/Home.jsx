import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { FiCalendar, FiClock, FiArrowUpRight, FiChevronLeft, FiChevronRight, FiRefreshCw, FiAlertCircle } from 'react-icons/fi';
import Layout from '../components/Layout';
import api from '../api';
import '../App.css';

const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const formatTime = (value) => value ? String(value).slice(0, 5) : '—';

export default function Home() {
  const [timetable, setTimetable] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [monthDate, setMonthDate] = useState(() => new Date(new Date().getFullYear(), new Date().getMonth(), 1));
  const [selectedDate, setSelectedDate] = useState(() => new Date().toISOString().slice(0, 10));
  const today = new Date();
  const username = localStorage.getItem('username') || 'Staff member';

  const loadTimetable = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await api.get('/get_timetable/');
      setTimetable(Array.isArray(response.data) ? response.data : (response.data?.results || []));
    } catch (err) {
      setError(err.response?.data?.detail || err.response?.data?.error || 'We could not load your timetable. Check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { loadTimetable(); }, [loadTimetable]);

  const selectedDateObject = new Date(`${selectedDate}T00:00:00`);
  const selectedWeekday = selectedDateObject.toLocaleDateString('en-US', { weekday: 'long' });
  const daySchedule = useMemo(() => timetable.filter((item) => (item.day || '').toLowerCase() === selectedWeekday.toLowerCase()).sort((a, b) => (a.start_time || '').localeCompare(b.start_time || '')), [timetable, selectedWeekday]);
  const monthLabel = monthDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  const firstDay = new Date(monthDate.getFullYear(), monthDate.getMonth(), 1).getDay();
  const daysInMonth = new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 0).getDate();
  const miniCalendarDays = Array.from({ length: firstDay + daysInMonth }, (_, index) => index < firstDay ? null : index - firstDay + 1);
  const shiftMonth = (amount) => setMonthDate((current) => new Date(current.getFullYear(), current.getMonth() + amount, 1));
  const pickDate = (day) => setSelectedDate(`${monthDate.getFullYear()}-${String(monthDate.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`);
  const displayName = username.replace(/[._-]/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());

  return (
    <Layout>
      <div className="dashboard-page">
        <section className="welcome-row">
          <div><div className="eyebrow">YOUR WORKSPACE</div><h1>Good {today.getHours() < 12 ? 'morning' : today.getHours() < 17 ? 'afternoon' : 'evening'}, {displayName.split(' ')[0]}.</h1><p>Keep your schedule in sync and make room for what matters.</p></div>
          <Link to="/home/meetingslots" className="button button-primary"><FiCalendar /> Find a meeting time <FiArrowUpRight /></Link>
        </section>

        <section className="summary-grid" aria-label="Schedule summary">
          <article className="summary-card"><div className="summary-icon summary-icon-red"><FiCalendar /></div><div><span className="summary-label">Weekly timetable</span><strong>{isLoading ? '—' : timetable.length}</strong><span className="summary-footnote">scheduled class slots</span></div></article>
          <article className="summary-card"><div className="summary-icon summary-icon-grey"><FiClock /></div><div><span className="summary-label">Selected day</span><strong>{selectedDateObject.toLocaleDateString('en-US', { day: 'numeric', month: 'short' })}</strong><span className="summary-footnote">{selectedWeekday}</span></div></article>
          <article className="summary-card"><div className="summary-icon summary-icon-soft"><FiCalendar /></div><div><span className="summary-label">Classes that day</span><strong>{isLoading ? '—' : daySchedule.length}</strong><span className="summary-footnote">from your saved timetable</span></div></article>
        </section>

        {error && <div className="alert alert-error" role="alert"><FiAlertCircle /><span>{error}</span><button className="text-button" onClick={loadTimetable}><FiRefreshCw /> Retry</button></div>}

        <div className="dashboard-grid">
          <section className="panel calendar-panel">
            <div className="panel-heading"><div><span className="eyebrow">PLAN YOUR WEEK</span><h2>Calendar</h2><p>Select a date to view its timetable.</p></div><Link className="subtle-link" to="/home/calendar">Full calendar <FiArrowUpRight /></Link></div>
            <div className="mini-calendar-toolbar"><strong>{monthLabel}</strong><div className="calendar-toolbar-actions"><button aria-label="Previous month" onClick={() => shiftMonth(-1)}><FiChevronLeft /></button><button aria-label="Next month" onClick={() => shiftMonth(1)}><FiChevronRight /></button></div></div>
            <div className="mini-calendar-grid mini-calendar-weekdays">{weekdays.map((day) => <span key={day}>{day}</span>)}</div>
            <div className="mini-calendar-grid mini-calendar-dates">{miniCalendarDays.map((day, index) => {
              if (!day) return <span className="mini-calendar-empty" key={`empty-${index}`} />;
              const dateKey = `${monthDate.getFullYear()}-${String(monthDate.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
              const isToday = dateKey === today.toISOString().slice(0, 10);
              const isSelected = dateKey === selectedDate;
              return <button key={dateKey} className={`mini-calendar-date ${isToday ? 'is-today' : ''} ${isSelected ? 'is-selected' : ''}`} onClick={() => pickDate(day)} aria-pressed={isSelected}>{day}</button>;
            })}</div>
            <div className="calendar-legend"><span><i className="legend-dot legend-dot-red" /> Selected date</span><span><i className="legend-dot legend-dot-outline" /> Today</span></div>
          </section>

          <section className="panel schedule-panel">
            <div className="panel-heading"><div><span className="eyebrow">YOUR TIMETABLE</span><h2>{selectedDateObject.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</h2><p>Classes saved to your staff timetable.</p></div><span className="schedule-count">{daySchedule.length} {daySchedule.length === 1 ? 'class' : 'classes'}</span></div>
            {isLoading ? <div className="loading-state"><span className="loading-spinner" /> Loading your schedule…</div> : daySchedule.length ? <div className="schedule-list">{daySchedule.map((item, index) => <article className="schedule-item" key={`${item.id || item.class_room || 'class'}-${index}`}><div className="schedule-time"><strong>{formatTime(item.start_time)}</strong><span>{formatTime(item.end_time)}</span></div><div className="schedule-timeline"><span /></div><div className="schedule-details"><strong>{item.subject || item.class_name || item.class_room || 'Scheduled class'}</strong><span>{item.class_room ? `Room ${item.class_room}` : 'Room not specified'}</span></div></article>)}</div> : <div className="empty-state"><div className="empty-state-icon"><FiCalendar /></div><strong>No classes listed for this day</strong><p>Your saved timetable has no entries for {selectedWeekday}. Choose another date or check back when your timetable is updated.</p></div>}
            <div className="panel-bottom-link"><Link to="/home/meetingslots">Check faculty availability <FiArrowUpRight /></Link></div>
          </section>
        </div>

        <section className="panel timetable-panel"><div className="panel-heading"><div><span className="eyebrow">REFERENCE</span><h2>Your weekly timetable</h2><p>All recurring class slots currently saved to your account.</p></div><button className="icon-button" onClick={loadTimetable} aria-label="Refresh timetable"><FiRefreshCw /></button></div>
          {isLoading ? <div className="loading-state"><span className="loading-spinner" /> Loading timetable…</div> : timetable.length ? <div className="table-scroll"><table className="data-table"><thead><tr><th>Day</th><th>Time</th><th>Class / room</th></tr></thead><tbody>{[...timetable].sort((a, b) => weekdays.indexOf((a.day || '').slice(0, 3)) - weekdays.indexOf((b.day || '').slice(0, 3)) || (a.start_time || '').localeCompare(b.start_time || '')).map((entry, index) => <tr key={entry.id || `${entry.day}-${entry.start_time}-${index}`}><td><span className="day-pill">{entry.day || '—'}</span></td><td>{formatTime(entry.start_time)} – {formatTime(entry.end_time)}</td><td>{entry.class_room || entry.subject || '—'}</td></tr>)}</tbody></table></div> : <div className="empty-state compact-empty"><strong>No timetable entries found</strong><p>When your timetable is added, it will appear here.</p></div>}
        </section>
      </div>
    </Layout>
  );
}
