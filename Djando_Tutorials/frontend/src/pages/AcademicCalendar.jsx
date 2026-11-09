import React, { useEffect, useState } from 'react';
import { FiArrowLeft, FiCalendar, FiSend } from 'react-icons/fi';
import Layout from '../components/Layout';
import api from '../api';
import '../App.css';

export default function AcademicCalendar() {
  const profile = JSON.parse(localStorage.getItem('profile') || '{}');
  const canPublish = Boolean(profile.department_head || profile.user?.is_staff);
  const [events, setEvents] = useState([]);
  const [form, setForm] = useState({ title: '', date: '', description: '', department: profile.department || '' });
  const [message, setMessage] = useState('');
  const loadEvents = async () => {
    const response = await api.get('/academic-events/');
    setEvents(Array.isArray(response.data) ? response.data : []);
  };
  useEffect(() => { loadEvents().catch(() => setMessage('Could not load academic events.')); }, []);
  const publish = async (event) => {
    event.preventDefault();
    try {
      await api.post('/academic-events/', form);
      setForm({ title: '', date: '', description: '', department: profile.department || '' });
      setMessage('Academic event published.');
      await loadEvents();
    } catch (error) {
      setMessage(error.response?.data?.error || 'Could not publish academic event.');
    }
  };
  return <Layout>
    <div className="content-page">
      <section className="page-intro"><div><div className="eyebrow">UNIVERSITY SCHEDULE</div><h1>Academic calendar</h1><p>Published academic events for your department and the university.</p></div><FiCalendar /></section>
      {canPublish && <section className="panel"><div className="panel-heading"><div><span className="eyebrow">PUBLISH EVENT</span><h2>Add an academic event</h2></div></div><form className="schedule-form" onSubmit={publish}><div className="field-group"><label htmlFor="academic-title">Title</label><input id="academic-title" value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} required /></div><div className="field-group"><label htmlFor="academic-date">Date</label><input id="academic-date" type="date" value={form.date} onChange={(event) => setForm({ ...form, date: event.target.value })} required /></div><div className="field-group"><label htmlFor="academic-description">Description</label><input id="academic-description" value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} /></div><button className="button button-primary" type="submit"><FiSend /> Publish</button></form></section>}
      {message && <div className="alert alert-success">{message}</div>}
      <section className="panel"><div className="panel-heading"><div><span className="eyebrow">PUBLISHED EVENTS</span><h2>Academic events</h2></div></div>{events.length ? <div className="month-events-list">{events.map((event) => <div className="month-event-row" key={event.id}><div className="month-event-date"><strong>{new Date(`${event.date}T00:00:00`).getDate()}</strong><span>{new Date(`${event.date}T00:00:00`).toLocaleDateString('en-US', { month: 'short' })}</span></div><div className="month-event-details"><strong>{event.title}</strong><span>{event.department || 'University-wide'} · {event.description || 'Academic event'}</span></div></div>)}</div> : <div className="empty-state"><FiCalendar /><strong>No published events</strong></div>}</section>
    </div>
  </Layout>;
}
