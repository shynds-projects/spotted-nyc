import { useState, useEffect } from 'react'
import { apiFetch } from '../api'
import PageHeader from '../components/PageHeader'

function formatDate(dateStr) {
  if (!dateStr) return 'Date unknown'
  const d = new Date(dateStr)
  if (isNaN(d)) return 'Date unknown'
  const days = Math.round((new Date() - d) / 86400000)
  if (days === 0) return 'Today'
  if (days === 1) return 'Yesterday'
  if (days < 7) return `${days}d ago`
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

export default function FeedPage({ city, setCity }) {
  const [venues, setVenues] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    apiFetch(`/api/feed?city=${city}`)
      .then((data) => {
        setVenues(Array.isArray(data) ? data : [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [city])

  const hotspots = venues.slice(0, 4)

  const sightings = venues
    .flatMap((v) =>
      (v.sightings || []).map((s) => ({
        id: s.id,
        celebrity_name: s.celebrity_name,
        spot_name: v.name,
        date_str: s.sighting_date,
        what_they_ate: s.what_they_ate,
        quote: s.quote,
        url: null,
      }))
    )
    .sort((a, b) => new Date(b.date_str || 0) - new Date(a.date_str || 0))
    .slice(0, 30)

  return (
    <div className="page feed-page">
      <PageHeader city={city} setCity={setCity} />
      <main className="page-main">
        <div className="section-header">
          <span className="caps-label">Premier Hotspots</span>
          <span className="caps-label">
            01 — {String(hotspots.length).padStart(2, '0')}
          </span>
        </div>

        {loading ? (
          <div className="loading-text">Loading…</div>
        ) : hotspots.length === 0 ? (
          <div className="empty-text">
            No hotspots yet — run the pipeline to populate data.
          </div>
        ) : (
          <div className="grid-container">
            {hotspots.map((v) => (
              <div key={v.id} className="grid-card">
                <div className="grid-image-wrap">
                  {v.photo_url ? (
                    <img src={v.photo_url} alt={v.name} />
                  ) : (
                    <div className="grid-image-placeholder" />
                  )}
                </div>
                <div className="restaurant-meta">
                  <span className="caps-label" style={{ fontSize: '8px' }}>
                    {[v.neighborhood, v.cuisine].filter(Boolean).join(' • ') ||
                      'NYC'}
                  </span>
                  <h3 className="restaurant-title">{v.name}</h3>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="section-header section-header-bordered">
          <span className="caps-label">Recent Sightings</span>
        </div>

        {sightings.length === 0 ? (
          <div className="empty-text">No sightings yet.</div>
        ) : (
          <div className="sightings-list">
            {sightings.map((s) => (
              <div key={s.id} className="sighting-item">
                <div className="sighting-header">
                  <span className="celeb-name">{s.celebrity_name}</span>
                  <span className="caps-label">{formatDate(s.date_str)}</span>
                </div>
                <h2 className="spot-name">{s.spot_name}</h2>
                {(s.what_they_ate || s.quote) && (
                  <p className="order-desc">
                    &ldquo;{s.what_they_ate || s.quote}&rdquo;
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
