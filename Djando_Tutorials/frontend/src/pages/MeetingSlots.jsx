import React, { useEffect, useState } from 'react';
import { FiAlertCircle, FiCalendar, FiCheckCircle, FiClock, FiSearch, FiSend, FiUsers } from 'react-icons/fi';
import Layout from '../components/Layout';
import api from '../api';
import '../App.css';

const timeOptions = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00'];
const today = new Date().toISOString().slice(0, 10);

export default function MeetingSlots() {
  const [mode, setMode] = useState('time');
  const [selectedDate, setSelectedDate] = useState(today);
  const [startTime, setStartTime] = useState('10:00');
  const [endTime, setEndTime] = useState('11:00');
  const [availableFaculty, setAvailableFaculty] = useState([]);
  const [busyFaculty, setBusyFaculty] = useState([]);
  const [facultyQuery, setFacultyQuery] = useState('');
  const [facultySuggestions, setFacultySuggestions] = useState([]);
  const [selectedFaculty, setSelectedFaculty] = useState([]);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [isLoadingSlots, setIsLoadingSlots] = useState(false);
  const [title, setTitle] = useState('');
  const [agenda, setAgenda] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [hasSearched, setHasSearched] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    let active = true;
    if (!facultyQuery.trim()) { setFacultySuggestions([]); return undefined; }
    const timer = setTimeout(async () => {
      try {
        const response = await api.get('/faculty/search/', { params: { q: facultyQuery } });
        if (active) setFacultySuggestions(Array.isArray(response.data) ? response.data : []);
      } catch (err) {
        if (active) setError(err.response?.data?.error || 'Could not search faculty.');
      }
    }, 250);
    return () => { active = false; clearTimeout(timer); };
  }, [facultyQuery]);

  useEffect(() => {
    if (mode !== 'faculty' || !selectedFaculty.length || !selectedDate) {
      setAvailableSlots([]);
      return undefined;
    }
    let active = true;
    setIsLoadingSlots(true);
    setError('');
    api.get('/faculty/available-slots/', {
      params: { usernames: selectedFaculty.map((faculty) => faculty.username).join(','), date: selectedDate },
    }).then((response) => {
      if (active) {
        setAvailableSlots(response.data?.slots || []);
        if (response.data?.message) setError(response.data.message);
      }
    }).catch((err) => {
      if (active) setError(err.response?.data?.error || 'Could not load available slots.');
    }).finally(() => {
      if (active) setIsLoadingSlots(false);
    });
    return () => { active = false; };
  }, [mode, selectedDate, selectedFaculty]);

  const addFaculty = (faculty) => {
    if (!selectedFaculty.some((item) => item.username === faculty.username)) setSelectedFaculty((current) => [...current, faculty]);
    setFacultyQuery('');
    setFacultySuggestions([]);
  };

  const selectSlot = (slot) => {
    setStartTime(slot.start_time);
    setEndTime(slot.end_time);
    setNotice('');
  };

  const searchByTime = async (event) => {
    event.preventDefault();
    if (!selectedDate || !startTime || !endTime || startTime >= endTime) { setError('Choose a valid date and time window.'); return; }
    setError(''); setNotice(''); setIsSearching(true); setHasSearched(false);
    try {
      const response = await api.get('/get_faculty_availability/', { params: { date: selectedDate, start_time: startTime, end_time: endTime } });
      setAvailableFaculty(response.data?.available_faculty || []);
      setBusyFaculty(response.data?.busy_faculty || []);
      setHasSearched(true);
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.detail || 'Could not check availability.');
    } finally { setIsSearching(false); }
  };

  const scheduleMeeting = async (event) => {
    event.preventDefault();
    setError(''); setNotice('');
    try {
      await api.post('/scheduled-meetings/', {
        title, agenda, date: selectedDate, start_time: startTime, end_time: endTime,
        participant_usernames: selectedFaculty.map((faculty) => faculty.username),
      });
      setNotice('Meeting scheduled. The invited faculty will see a notification in their workspace.');
      setTitle(''); setAgenda(''); setSelectedFaculty([]);
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.detail || 'Could not schedule the meeting.');
    }
  };

  const currentUsername = localStorage.getItem('username');
  const chooseFromResults = (faculty) => addFaculty(faculty);
  const availableOthers = availableFaculty.filter((faculty) => faculty.username !== currentUsername);
  const busyOthers = busyFaculty.filter((faculty) => faculty.username !== currentUsername);

  return <Layout>
    <div className="content-page meeting-page">
      <section className="page-intro"><div><div className="eyebrow">COORDINATE TOGETHER</div><h1>Plan a meeting</h1><p>Find the right faculty and send invitations from one workspace.</p></div><div className="page-intro-icon"><FiUsers /></div></section>
      <section className="panel availability-search-panel">
        <div className="search-mode-tabs" role="tablist">
          <button className={mode === 'time' ? 'search-mode-active' : ''} onClick={() => setMode('time')}><FiClock /> When would you like to meet?</button>
          <button className={mode === 'faculty' ? 'search-mode-active' : ''} onClick={() => setMode('faculty')}><FiUsers /> Whom would you like to schedule with?</button>
        </div>
        <div className="panel-heading"><div><span className="eyebrow">AVAILABILITY SEARCH</span><h2>{mode === 'time' ? 'When would you like to meet?' : 'Whom would you like to schedule with?'}</h2><p>{mode === 'time' ? 'Find faculty who are free during a date and time window.' : 'Type a few letters to find and select faculty members.'}</p></div></div>
        {mode === 'time' ? <form className="availability-form" onSubmit={searchByTime}>
          <div className="field-group"><label htmlFor="selected-date"><FiCalendar /> Date</label><input id="selected-date" type="date" value={selectedDate} min={today} onChange={(event) => setSelectedDate(event.target.value)} required /></div>
          <div className="field-group"><label htmlFor="start-time"><FiClock /> Start time</label><select id="start-time" value={startTime} onChange={(event) => setStartTime(event.target.value)}>{timeOptions.slice(0, -1).map((time) => <option key={time}>{time}</option>)}</select></div>
          <div className="field-group"><label htmlFor="end-time"><FiClock /> End time</label><select id="end-time" value={endTime} onChange={(event) => setEndTime(event.target.value)}>{timeOptions.slice(1).map((time) => <option key={time}>{time}</option>)}</select></div>
          <button className="button button-primary search-submit" type="submit" disabled={isSearching}>{isSearching ? 'Checking…' : <><FiSearch /> Check availability</>}</button>
        </form> : <div className="faculty-first-flow">
          <div className="faculty-search-field field-group"><label htmlFor="faculty-search"><FiSearch /> Faculty name or staff ID</label><input id="faculty-search" value={facultyQuery} onChange={(event) => setFacultyQuery(event.target.value)} placeholder="Start typing a name or staff ID…" autoComplete="off" />{facultySuggestions.length > 0 && <div className="faculty-suggestions">{facultySuggestions.map((faculty) => <button type="button" key={faculty.username} onClick={() => addFaculty(faculty)}><strong>{faculty.name}</strong><small>{faculty.staff_id} · {faculty.department}</small></button>)}</div>}</div>
          {selectedFaculty.length > 0 && <div className="selected-faculty-list">{selectedFaculty.map((faculty) => <button type="button" key={faculty.username} onClick={() => setSelectedFaculty((current) => current.filter((item) => item.username !== faculty.username))}>{faculty.name || faculty.username} ×</button>)}</div>}
          <div className="field-group faculty-date-step"><label htmlFor="faculty-date"><FiCalendar /> Then choose a date</label><input id="faculty-date" type="date" value={selectedDate} min={today} onChange={(event) => setSelectedDate(event.target.value)} disabled={!selectedFaculty.length} /></div>
          <div className="available-slots-step"><div className="step-heading"><FiClock /><strong>Available slots</strong><span>{selectedFaculty.length ? `for ${selectedDate}` : 'Select faculty first'}</span></div>{isLoadingSlots ? <div className="loading-state"><span className="loading-spinner" /> Loading available slots…</div> : availableSlots.length ? <div className="available-slot-list">{availableSlots.map((slot) => <button type="button" className={startTime === slot.start_time && endTime === slot.end_time ? 'slot-button slot-button-selected' : 'slot-button'} key={`${slot.start_time}-${slot.end_time}`} onClick={() => selectSlot(slot)}><FiClock /> {slot.start_time} – {slot.end_time}</button>)}</div> : <div className="results-placeholder compact-empty"><FiClock /><p>{selectedFaculty.length ? 'No free slots are available on this date.' : 'Select a faculty member to see available slots.'}</p></div>}</div>
        </div>}
        {error && <div className="alert alert-error" role="alert"><FiAlertCircle /><span>{error}</span></div>}
        {notice && <div className="alert alert-success" role="status"><FiCheckCircle /><span>{notice}</span></div>}
      </section>

      {mode === 'time' && <div className="availability-results-grid">
        <section className="panel faculty-results-panel"><div className="results-panel-title"><div className="results-status-icon available-status"><FiCheckCircle /></div><div><h3>Available faculty</h3><p>Select people to invite</p></div><span className="result-count result-count-available">{hasSearched ? availableOthers.length : '—'}</span></div>{!hasSearched ? <div className="results-placeholder"><FiSearch /><p>Search a date and time to see available faculty.</p></div> : availableOthers.length ? <ul className="faculty-list">{availableOthers.map((faculty) => <li key={faculty.username}><span className="faculty-avatar">{faculty.username.slice(0, 1).toUpperCase()}</span><span className="faculty-info"><strong>{faculty.username}</strong><small>{faculty.department}</small></span><button className="text-button" onClick={() => chooseFromResults(faculty)}>Invite</button></li>)}</ul> : <div className="results-placeholder"><FiUsers /><p>No available faculty found.</p></div>}</section>
        <section className="panel faculty-results-panel"><div className="results-panel-title"><div className="results-status-icon busy-status"><FiClock /></div><div><h3>Busy faculty</h3><p>Staff with a detected conflict</p></div><span className="result-count result-count-busy">{hasSearched ? busyOthers.length : '—'}</span></div>{busyOthers.length ? <ul className="faculty-list">{busyOthers.map((faculty) => <li key={faculty.username}><span className="faculty-avatar faculty-avatar-muted">{faculty.username.slice(0, 1).toUpperCase()}</span><span className="faculty-info"><strong>{faculty.username}</strong><small>{faculty.department}</small></span><span className="status-pill status-busy">Busy</span></li>)}</ul> : <div className="results-placeholder"><FiClock /><p>Busy faculty will appear after a time search.</p></div>}</section>
      </div>}

      <section className="panel schedule-meeting-panel"><div className="panel-heading"><div><span className="eyebrow">SEND INVITATIONS</span><h2>Schedule with selected faculty</h2><p>Choose the meeting details and notify everyone together.</p></div><FiSend /></div>{selectedFaculty.length ? <div className="selected-faculty-summary"><strong>{selectedFaculty.map((faculty) => faculty.name || faculty.username).join(', ')}</strong><span>{selectedDate} · {startTime}–{endTime}</span></div> : <div className="results-placeholder compact-empty"><FiUsers /><p>Search by name or use the availability results to select faculty.</p></div>}<form className="schedule-form" onSubmit={scheduleMeeting}><div className="field-group"><label htmlFor="meeting-title">Purpose of meeting</label><input id="meeting-title" value={title} onChange={(event) => setTitle(event.target.value)} placeholder="e.g. Curriculum planning" required /></div><div className="field-group"><label htmlFor="meeting-agenda">Agenda (optional)</label><input id="meeting-agenda" value={agenda} onChange={(event) => setAgenda(event.target.value)} placeholder="What should everyone prepare?" /></div><button className="button button-primary" type="submit" disabled={!selectedFaculty.length || (mode === 'faculty' && !availableSlots.some((slot) => slot.start_time === startTime && slot.end_time === endTime))}><FiSend /> Schedule meeting</button></form></section>
    </div>
  </Layout>;
}
