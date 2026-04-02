const cityNames = {
  nyc: 'New York',
  philadelphia: 'Philadelphia',
}

export default function PageHeader({ city, setCity }) {
  function toggleCity() {
    setCity(city === 'nyc' ? 'philadelphia' : 'nyc')
  }

  return (
    <header className="page-header">
      <div className="city-toggle">
        <span className="caps-label">Currently Viewing</span>
        <div className="city-selector" onClick={toggleCity}>
          {cityNames[city]}
        </div>
      </div>
      <div className="status-dot" />
    </header>
  )
}
