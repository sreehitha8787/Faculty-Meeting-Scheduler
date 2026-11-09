import React, { useEffect, useState } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { FiBell, FiCalendar, FiClock, FiHome, FiLogOut, FiMenu, FiX, FiSettings, FiChevronRight, FiList } from 'react-icons/fi';
import api from '../api';
import muLogo from '../assets/MU Logo.jpeg';

const navigation = [
  { to: '/home', label: 'Dashboard', icon: FiHome, end: true },
  { to: '/home/timetable', label: 'Weekly timetable', icon: FiList },
  { to: '/home/meetingslots', label: 'Meeting slots', icon: FiClock },
  { to: '/home/calendar', label: 'Calendar', icon: FiCalendar },
  { to: '/home/academic-calendar', label: 'Academic calendar', icon: FiCalendar },
];

const decodeVapidKey = (value) => {
  const padding = '='.repeat((4 - (value.length % 4)) % 4);
  const base64 = (value + padding).replace(/-/g, '+').replace(/_/g, '/');
  const raw = window.atob(base64);
  return Uint8Array.from(raw, (character) => character.charCodeAt(0));
};

export default function Layout({ children }) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const [notificationOpen, setNotificationOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [pushStatus, setPushStatus] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const profile = JSON.parse(localStorage.getItem('profile') || '{}');
  const username = localStorage.getItem('username') || 'Staff member';
  const initials = username.split(/[._\s-]/).filter(Boolean).slice(0, 2).map((part) => part[0]?.toUpperCase()).join('') || 'MU';
  const pageTitle = navigation.find((item) => item.to === location.pathname)?.label || 'Staff calendar';

  useEffect(() => {
    api.get('/notifications/').then((response) => setNotifications(Array.isArray(response.data) ? response.data : [])).catch((error) => console.error('Could not load notifications.', error));
  }, [location.pathname]);

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (!token) return undefined;
    const socketProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socket = new WebSocket(`${socketProtocol}://${window.location.hostname}:8000/ws/notifications/?token=${encodeURIComponent(token)}`);
    socket.onmessage = (event) => {
      const notification = JSON.parse(event.data);
      setNotifications((current) => [{ ...notification, is_read: false, created_at: new Date().toISOString() }, ...current]);
    };
    return () => socket.close();
  }, []);

  const unreadCount = notifications.filter((item) => !item.is_read).length;
  const openNotifications = async () => {
    setNotificationOpen((open) => !open);
    if (unreadCount) {
      try {
        await api.patch('/notifications/');
        setNotifications((current) => current.map((item) => ({ ...item, is_read: true })));
      } catch (error) {
        console.error('Could not mark notifications as read.', error);
      }
    }
  };

  const respondToInvitation = async (meetingId, response) => {
    try {
      await api.patch(`/scheduled-meetings/${meetingId}/response/`, { response });
      setNotifications((current) => current.map((item) => item.meeting_id === meetingId ? { ...item, can_respond: false, message: `Invitation ${response}.` } : item));
    } catch (error) {
      console.error('Could not respond to meeting invitation.', error);
    }
  };

  const enableBrowserNotifications = async () => {
    try {
      if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        setPushStatus('Browser push notifications are not supported here.');
        return;
      }
      const publicKey = import.meta.env.VITE_VAPID_PUBLIC_KEY;
      if (!publicKey) {
        setPushStatus('Browser notifications need VITE_VAPID_PUBLIC_KEY.');
        return;
      }
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        setPushStatus('Browser notification permission was not granted.');
        return;
      }
      const registration = await navigator.serviceWorker.register('/push-sw.js');
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: decodeVapidKey(publicKey),
      });
      await api.post('/push-subscriptions/', subscription.toJSON());
      setPushStatus('Browser notifications enabled.');
    } catch (error) {
      console.error('Could not enable browser notifications.', error);
      setPushStatus('Could not enable browser notifications.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('username');
    localStorage.removeItem('profile');
    navigate('/', { replace: true });
  };

  return (
    <div className="app-shell">
      {mobileNavOpen && <button className="mobile-nav-scrim" aria-label="Close navigation" onClick={() => setMobileNavOpen(false)} />}
      <aside className={`app-sidebar ${mobileNavOpen ? 'app-sidebar--open' : ''}`}>
        <div className="brand-lockup">
          <img src={muLogo} alt="Mahindra University" className="brand-logo" />
          <div className="brand-caption">STAFF CALENDAR</div>
          <button className="mobile-close-button" aria-label="Close menu" onClick={() => setMobileNavOpen(false)}><FiX /></button>
        </div>

        <div className="sidebar-section-label">WORKSPACE</div>
        <nav className="primary-nav" aria-label="Main navigation">
          {navigation.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.end} onClick={() => setMobileNavOpen(false)} className={({ isActive }) => `nav-link ${isActive ? 'nav-link--active' : ''}`}>
              <item.icon className="nav-icon" aria-hidden="true" />
              <span>{item.label}</span>
              {item.label === pageTitle && <FiChevronRight className="nav-chevron" aria-hidden="true" />}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-help-card">
            <div className="help-card-icon"><FiCalendar /></div>
            <strong>Plan together</strong>
            <p>Find time for the meetings that matter.</p>
          </div>
          <button className="sidebar-logout" onClick={handleLogout}><FiLogOut /> <span>Sign out</span></button>
          <div className="sidebar-footer">Mahindra University · Staff workspace</div>
        </div>
      </aside>

      <div className="app-main-column">
        <header className="app-topbar">
          <button className="mobile-menu-button" aria-label="Open navigation" onClick={() => setMobileNavOpen(true)}><FiMenu /></button>
          <div className="topbar-breadcrumb"><span>Workspace</span><FiChevronRight /><strong>{pageTitle}</strong></div>
          <div className="topbar-actions">
            <div className="notification-wrap">
              <button className="notification-button" onClick={openNotifications} aria-label={`Notifications${unreadCount ? `, ${unreadCount} unread` : ''}`} aria-expanded={notificationOpen}><FiBell />{unreadCount > 0 && <span className="notification-badge">{unreadCount > 9 ? '9+' : unreadCount}</span>}</button>
              {notificationOpen && <div className="notification-popover"><div className="notification-heading"><strong>Notifications</strong><span>{notifications.length} recent</span></div><button className="enable-push-button" onClick={enableBrowserNotifications}><FiBell /> Enable browser alerts</button>{pushStatus && <div className="push-status">{pushStatus}</div>}{notifications.length ? notifications.map((item) => <div className={`notification-item ${item.is_read ? '' : 'notification-item-unread'}`} key={item.id}><FiBell /><span>{item.message}<small>{new Date(item.created_at).toLocaleString()}</small>{item.can_respond && <span className="notification-actions"><button onClick={() => respondToInvitation(item.meeting_id, 'accepted')}>Accept</button><button onClick={() => respondToInvitation(item.meeting_id, 'declined')}>Reject</button></span>}</span></div>) : <div className="notification-empty">No notifications yet.</div>}</div>}
            </div>
            <div className="topbar-user-wrap">
              <button className="user-menu-button" onClick={() => setProfileMenuOpen((open) => !open)} aria-expanded={profileMenuOpen}>
                <span className="user-avatar">{initials}</span>
                <span className="user-menu-name">{username}</span>
                <FiSettings className="user-menu-settings" />
              </button>
              {profileMenuOpen && <div className="user-popover"><div className="popover-user"><span className="user-avatar">{initials}</span><div><strong>{profile.user?.full_name || username}</strong><small>{profile.user?.email || 'Email not available'}</small></div></div><div className="popover-details"><div><span>Username</span><strong>{profile.user?.username || username}</strong></div><div><span>Teaching field</span><strong>{profile.department || 'Not specified'}</strong></div><div><span>Position</span><strong>{profile.faculty_position || 'Faculty member'}</strong></div><div><span>Staff ID</span><strong>{profile.staff_id || 'Not specified'}</strong></div></div><button onClick={handleLogout}><FiLogOut /> Sign out</button></div>}
            </div>
          </div>
        </header>
        <main className="page-content" onClick={() => profileMenuOpen && setProfileMenuOpen(false)}>{children}</main>
        <footer className="app-footer"><span>Mahindra University</span><span>Staff Calendar Workspace</span></footer>
      </div>
    </div>
  );
}
