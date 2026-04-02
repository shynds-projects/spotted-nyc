import { useState } from 'react'
import NavBar from './components/NavBar'
import FeedPage from './pages/FeedPage'
import NewsPage from './pages/NewsPage'
import ProfilePage from './pages/ProfilePage'

export default function App() {
  const [activeTab, setActiveTab] = useState('feed')
  const [city, setCity] = useState('nyc')

  return (
    <div className="app-shell">
      {activeTab === 'feed' && <FeedPage city={city} setCity={setCity} />}
      {activeTab === 'news' && <NewsPage city={city} setCity={setCity} />}
      {activeTab === 'profile' && <ProfilePage />}
      <NavBar activeTab={activeTab} onTabChange={setActiveTab} />
    </div>
  )
}
