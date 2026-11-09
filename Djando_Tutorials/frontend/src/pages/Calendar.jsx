import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { FiCalendar, FiChevronLeft, FiChevronRight, FiClock, FiArrowUpRight, FiAlertCircle, FiRefreshCw } from 'react-icons/fi';
import Layout from '../components/Layout';
import api from '../api';
import '../App.css';

const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const timeText = (value) => value ? String(value).slice(0, 5) : 'Time not set';

export default function Calendar() {
  const [currentMonthDate, setCurrentMonthDate] = useState(() => new Date(new Date().getFullYear(), new Date().getMonth(), 1));
  const [busySlots, setBusySlots] = useState([]);
  const [scheduledMeetings, setScheduledMeetings] = useState([]);
  const [holidays, setHolidays] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedDate, setSelectedDate] = useState(() => new Date().toISOString().slice(0, 10));

  const fetchBusySlots = useCallback(async () => {
    setIsLoading(true); setError('');
    try {
      const [response, holidayResponse, scheduledResponse] = await Promise.all([api.get('/meetings/'), api.get('/holidays/'), api.get('/scheduled-meetings/')]);
      setHolidays(Array.isArray(holidayResponse.data) ? holidayResponse.data : []);
      const rows = Array.isArray(response.data) ? response.data : (response.data?.results || []);
      setBusySlots(rows.filter((slot) => slot.is_available === false));
      setScheduledMeetings(Array.isArray(scheduledResponse.data) ? scheduledResponse.data.filter((meeting) => ['pending', 'accepted'].includes(meeting.status)) : []);
    } catch (err) {
      setError(err.response?.data?.detail || err.response?.data?.error || 'Could not load saved calendar entries. Please try again.');
    } finally { setIsLoading(false); }
  }, []);
  useEffect(() => { fetchBusySlots(); }, [fetchBusySlots]);

  const monthLabel = currentMonthDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  const firstDay = new Date(currentMonthDate.getFullYear(), currentMonthDate.getMonth(), 1).getDay();
  const daysInMonth = new Date(currentMonthDate.getFullYear(), currentMonthDate.getMonth() + 1, 0).getDate();
  const slotsByDate = useMemo(() => busySlots.reduce((grouped, slot) => {
    if (slot.date) { grouped[slot.date] ||= []; grouped[slot.date].push(slot); }
    return grouped;
  }, {}), [busySlots]);
  const monthPrefix = `${currentMonthDate.getFullYear()}-${String(currentMonthDate.getMonth() + 1).padStart(2, '0')}-`;
  const monthEntries = useMemo(() => {
    const dates = new Set([
      ...Object.keys(slotsByDate).filter((date) => date.startsWith(monthPrefix)),
      ...scheduledMeetings.map((meeting) => meeting.date).filter((date) => date.startsWith(monthPrefix)),
    ]);
    return [...dates].sort().map((date) => ({
      date,
      entries: slotsByDate[date] || [],
      meetings: scheduledMeetings.filter((meeting) => meeting.date === date),
    }));
  }, [monthPrefix, scheduledMeetings, slotsByDate]);
  const selectedEntries = slotsByDate[selectedDate] || [];
  const selectedMeetings = scheduledMeetings.filter((meeting) => meeting.date === selectedDate);
  const holidaysByDate = useMemo(() => Object.fromEntries(holidays.map((holiday) => [holiday.date, holiday])), [holidays]);
  const selectedHoliday = holidaysByDate[selectedDate];
  const calendarDays = Array.from({ length: firstDay + daysInMonth }, (_, index) => index < firstDay ? null : index - firstDay + 1);
  const todayKey = new Date().toISOString().slice(0, 10);
  const changeMonth = (offset) => setCurrentMonthDate((current) => new Date(current.getFullYear(), current.getMonth() + offset, 1));
  const selectDay = (day) => setSelectedDate(`${currentMonthDate.getFullYear()}-${String(currentMonthDate.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`);

  return <Layout>
    <div className="content-page calendar-page">
      <section className="page-intro"><div><div className="eyebrow">YOUR SCHEDULE</div><h1>Calendar</h1><p>View your schedule, public holidays and saved busy times.</p></div><Link to="/home/meetingslots" className="button button-primary"><FiCalendar /> Find a meeting time <FiArrowUpRight /></Link></section>
      {error && <div className="alert alert-error" role="alert"><FiAlertCircle /><span>{error}</span><button className="text-button" onClick={fetchBusySlots}><FiRefreshCw /> Retry</button></div>}
      <div className="full-calendar-layout">
        <section className="panel full-calendar-panel">
          <div className="full-calendar-toolbar"><div><h2>{monthLabel}</h2><p>Choose a date to see saved busy times.</p></div><div className="calendar-toolbar-actions"><button onClick={() => changeMonth(-1)} aria-label="Previous month"><FiChevronLeft /></button><button className="today-button" onClick={() => { const now = new Date(); setCurrentMonthDate(new Date(now.getFullYear(), now.getMonth(), 1)); setSelectedDate(now.toISOString().slice(0, 10)); }}>Today</button><button onClick={() => changeMonth(1)} aria-label="Next month"><FiChevronRight /></button></div></div>
          <div className="full-calendar-grid full-calendar-weekdays">{weekdays.map((day) => <div key={day}>{day}</div>)}</div>
          <div className="full-calendar-grid full-calendar-dates">{calendarDays.map((day, index) => {
            if (!day) return <div key={`blank-${index}`} className="full-calendar-empty" />;
            const dateKey = `${currentMonthDate.getFullYear()}-${String(currentMonthDate.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const holiday = holidaysByDate[dateKey];
            const busyCount = slotsByDate[dateKey]?.length || 0;
            const meetingCount = scheduledMeetings.filter((meeting) => meeting.date === dateKey).length;
            return <button key={dateKey} className={`full-calendar-date ${dateKey === todayKey ? 'is-today' : ''} ${dateKey === selectedDate ? 'is-selected' : ''}`} onClick={() => selectDay(day)} aria-pressed={dateKey === selectedDate}><span className="date-number">{day}</span>{holiday && <span className="calendar-event-chip" title={holiday.name}><i /> Holiday</span>}{busyCount > 0 && <span className="calendar-event-chip"><i /> {busyCount} busy {busyCount === 1 ? 'slot' : 'slots'}</span>}{meetingCount > 0 && <span className="calendar-event-chip"><i /> {meetingCount} meeting{meetingCount === 1 ? '' : 's'}</span>}</button>;
          })}</div>
          <div className="calendar-legend"><span><i className="legend-dot legend-dot-red" /> Selected date</span><span><i className="legend-dot legend-dot-outline" /> Today</span><span><i className="legend-dot legend-dot-event" /> Saved busy time</span></div>
        </section>
        <aside className="panel selected-day-panel"><div className="selected-day-heading"><div className="selected-day-icon"><FiCalendar /></div><div><span className="eyebrow">SELECTED DAY</span><h2>{new Date(`${selectedDate}T00:00:00`).toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}</h2></div></div>
          {selectedHoliday && <div className="alert alert-error"><FiAlertCircle /><span><strong>PUBLIC HOLIDAY — {selectedHoliday.name}.</strong> Meeting scheduling is blocked for this date.</span></div>}
          {isLoading ? <div className="loading-state"><span className="loading-spinner" /> Loading entries…</div> : selectedEntries.length || selectedMeetings.length ? <div className="selected-day-list">{selectedMeetings.map((meeting) => <article className="selected-event" key={`meeting-${meeting.id}`}><div className="event-time-icon"><FiCalendar /></div><div><strong>{meeting.title}</strong><span>{timeText(meeting.start_time)} – {timeText(meeting.end_time)}</span><p>Meeting · {meeting.status}</p></div></article>)}{selectedEntries.slice().sort((a, b) => (a.start_time || '').localeCompare(b.start_time || '')).map((entry, index) => <article className="selected-event" key={entry.id || `${entry.start_time}-${index}`}><div className="event-time-icon"><FiClock /></div><div><strong>Busy time</strong><span>{timeText(entry.start_time)} – {timeText(entry.end_time)}</span>{entry.title && <p>{entry.title}</p>}</div></article>)}</div> : <div className="empty-state"><div className="empty-state-icon"><FiCalendar /></div><strong>No saved busy times</strong><p>There are no saved busy meeting slots for this date.</p></div>}
          <div className="selected-day-actions">{!selectedHoliday && <Link to="/home/meetingslots" className="button button-secondary">Check availability <FiArrowUpRight /></Link>}</div>
        </aside>
      </div>
      <section className="panel month-events-panel"><div className="panel-heading"><div><span className="eyebrow">MONTH OVERVIEW</span><h2>Scheduled activity</h2><p>Meetings and saved busy times for {monthLabel}.</p></div><span className="schedule-count">{monthEntries.reduce((count, item) => count + item.entries.length + item.meetings.length, 0)} entries</span></div>
        {isLoading ? <div className="loading-state"><span className="loading-spinner" /> Loading calendar entries…</div> : monthEntries.length ? <div className="month-events-list">{monthEntries.map(({ date, entries, meetings }) => <div className="month-event-row" key={date}><div className="month-event-date"><strong>{new Date(`${date}T00:00:00`).toLocaleDateString('en-US', { day: '2-digit' })}</strong><span>{new Date(`${date}T00:00:00`).toLocaleDateString('en-US', { month: 'short' })}</span></div><div className="month-event-details"><strong>{new Date(`${date}T00:00:00`).toLocaleDateString('en-US', { weekday: 'long' })}</strong>{meetings.map((meeting) => <span key={`meeting-${meeting.id}`}>{meeting.title}: {timeText(meeting.start_time)} – {timeText(meeting.end_time)}</span>)}{entries.map((entry, index) => <span key={entry.id || index}>{timeText(entry.start_time)} – {timeText(entry.end_time)}</span>)}</div><button className="text-button" onClick={() => { setSelectedDate(date); window.scrollTo({ top: 0, behavior: 'smooth' }); }}>View day <FiArrowUpRight /></button></div>)}</div> : <div className="empty-state compact-empty"><strong>No scheduled activity this month</strong><p>Scheduled meetings and saved busy meeting slots will appear here.</p></div>}
      </section>
      <p className="feature-note"><FiAlertCircle /> Public holiday dates come from the university holiday register. Confirm the approved university calendar before production use.</p>
    </div>
  </Layout>;
}
