import { useState } from 'react'

export default function ProfilePage() {
  const [notifications, setNotifications] = useState(true)
  const [newsletter, setNewsletter] = useState(false)

  return (
    <div className="page profile-page">
      <header className="profile-header">
        <div className="avatar-wrap">
          <svg
            width="80"
            height="80"
            viewBox="0 0 80 80"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle cx="40" cy="40" r="40" fill="#e0e0e0" />
            <circle cx="40" cy="30" r="14" fill="#bdbdbd" />
            <ellipse cx="40" cy="68" rx="22" ry="16" fill="#bdbdbd" />
          </svg>
        </div>
        <div className="user-info">
          <h1>Jane Doe</h1>
          <span className="user-handle">@diningNY</span>
        </div>
      </header>

      <main className="page-main">
        <div className="settings-section">
          <div className="section-title">
            <span className="caps-label">Saved Restaurants</span>
          </div>
          {[
            { name: 'Lucali', sub: 'Brooklyn • Pizza' },
            { name: 'Carbone', sub: 'Village • Italian' },
          ].map((r) => (
            <a key={r.name} href="#" className="list-item">
              <div className="list-item-content">
                <span className="item-main">{r.name}</span>
                <span className="item-sub">{r.sub}</span>
              </div>
              <span className="chevron">›</span>
            </a>
          ))}
        </div>

        <div className="settings-section">
          <div className="section-title">
            <span className="caps-label">Followed Cities</span>
          </div>
          <div className="pill-container">
            <div className="city-pill">New York</div>
            <div className="city-pill">Philadelphia</div>
            <div className="city-pill city-pill-add">+ Add City</div>
          </div>
        </div>

        <div className="settings-section">
          <div className="section-title">
            <span className="caps-label">Preferences</span>
          </div>
          <div className="list-item">
            <div className="list-item-content">
              <span className="item-main">Push Notifications</span>
              <span className="item-sub">Daily sighting alerts</span>
            </div>
            <label className="toggle">
              <input
                type="checkbox"
                checked={notifications}
                onChange={() => setNotifications(!notifications)}
              />
              <span className="slider" />
            </label>
          </div>
          <div className="list-item">
            <div className="list-item-content">
              <span className="item-main">Newsletter</span>
              <span className="item-sub">Weekly hotspots digest</span>
            </div>
            <label className="toggle">
              <input
                type="checkbox"
                checked={newsletter}
                onChange={() => setNewsletter(!newsletter)}
              />
              <span className="slider" />
            </label>
          </div>
        </div>

        <div className="settings-section">
          <div className="section-title">
            <span className="caps-label">Account</span>
          </div>
          <a href="#" className="list-item">
            <span className="item-main">Edit Profile</span>
            <span className="chevron">›</span>
          </a>
          <a href="#" className="list-item">
            <span className="item-main">Privacy Settings</span>
            <span className="chevron">›</span>
          </a>
          <a href="#" className="list-item">
            <span className="item-main" style={{ color: 'var(--accent)' }}>
              Log Out
            </span>
          </a>
        </div>
      </main>
    </div>
  )
}
