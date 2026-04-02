import { useState, useEffect } from 'react'
import { apiFetch } from '../api'
import PageHeader from '../components/PageHeader'

const sourceColors = {
  'Eater NY': '#ea6451',
  'Page Six': '#000',
  'New York Post': '#000',
  'Just Jared': '#e63946',
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  if (isNaN(d)) return ''
  const hours = Math.round((new Date() - d) / 3600000)
  if (hours < 1) return 'Just now'
  if (hours < 24) return `${hours}h ago`
  if (Math.round(hours / 24) === 1) return 'Yesterday'
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

export default function NewsPage({ city, setCity }) {
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    apiFetch(`/api/news?city=${city}`)
      .then((data) => {
        setArticles(Array.isArray(data) ? data : [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [city])

  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  })

  return (
    <div className="page news-page">
      <PageHeader city={city} setCity={setCity} />
      <main className="page-main">
        <div className="section-header">
          <span className="caps-label">The Latest Dispatch</span>
          <span className="caps-label">{today}</span>
        </div>

        {loading ? (
          <div className="loading-text">Loading…</div>
        ) : articles.length === 0 ? (
          <div className="empty-text">
            No news yet — run the pipeline to populate data.
          </div>
        ) : (
          <div className="news-list">
            {articles.map((a) => (
              <a
                key={a.id}
                href={a.source_url || '#'}
                target="_blank"
                rel="noreferrer"
                className="news-item"
              >
                <div className="news-content">
                  <div className="news-source-row">
                    <span
                      className="source-tag"
                      style={
                        sourceColors[a.outlet]
                          ? { color: sourceColors[a.outlet] }
                          : {}
                      }
                    >
                      {a.outlet}
                    </span>
                    <span className="caps-label" style={{ fontSize: '9px' }}>
                      {formatTime(a.published_at)}
                    </span>
                  </div>
                  <h2 className="news-headline">{a.headline}</h2>
                  {a.summary && (
                    <p className="news-excerpt">{a.summary}</p>
                  )}
                </div>
              </a>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
