import { useEffect, useState } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

const defaultForm = {
  budget: 25000,
  days: 5,
  travelers: 2,
  travel_type: 'family',
  interests: 'nature, adventure',
  location: 'India',
  climate: 'cool',
}

function App() {
  const [form, setForm] = useState(defaultForm)
  const [destinations, setDestinations] = useState([])
  const [selectedMapDestination, setSelectedMapDestination] = useState(null)
  const [dashboard, setDashboard] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [travelPlan, setTravelPlan] = useState(null)
  const [budgetEstimate, setBudgetEstimate] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchDestinations()
    fetchDashboard()
  }, [])

  const fetchDestinations = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/destinations`)
      const data = await res.json()
      const availableDestinations = data.destinations || []
      setDestinations(availableDestinations)
      setSelectedMapDestination(availableDestinations[0] || null)
    } catch (err) {
      setError('Backend is not responding. Please start the FastAPI server first.')
    }
  }

  const fetchDashboard = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/analytics/dashboard`)
      const data = await res.json()
      setDashboard(data.dashboard)
    } catch (err) {
      console.error(err)
    }
  }

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')

    try {
      const payload = {
        budget: Number(form.budget),
        days: Number(form.days),
        travelers: Number(form.travelers),
        travel_type: form.travel_type,
        interests: form.interests.split(',').map((item) => item.trim()).filter(Boolean),
        location: form.location,
        climate: form.climate,
      }

      const res = await fetch(`${API_BASE}/api/recommendations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to fetch recommendations')
      }

      const matched = data.recommendations || []
      setRecommendations(matched)

      if (matched[0]) {
        setSelectedMapDestination(matched[0])
        const destinationName = matched[0].destination_name
        await createTravelPlan(destinationName, payload)
        await estimateBudget(destinationName, payload)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const createTravelPlan = async (destinationName, payload) => {
    const planPayload = {
      destination_name: destinationName,
      days: Number(payload.days),
      travelers: Number(payload.travelers),
      travel_type: payload.travel_type,
      interests: payload.interests,
    }

    const res = await fetch(`${API_BASE}/api/travel-plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(planPayload),
    })
    const data = await res.json()
    setTravelPlan(data.travel_plan)
  }

  const estimateBudget = async (destinationName, payload) => {
    const budgetPayload = {
      destination_name: destinationName,
      days: Number(payload.days),
      travelers: Number(payload.travelers),
      travel_type: payload.travel_type,
    }

    const res = await fetch(`${API_BASE}/api/budget/estimate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(budgetPayload),
    })
    const data = await res.json()
    setBudgetEstimate(data.budget_estimate)
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">AI & Data Science Project</p>
          <h1>Tourism AI Decision Support</h1>
        </div>
        <button
          className="primary-btn"
          onClick={() => document.getElementById('traveler-preferences')?.scrollIntoView({ behavior: 'smooth' })}
        >
          Live Demo
        </button>
      </header>

      <section className="hero-card">
        <div>
          <p className="section-tag">Smart Travel Recommendation</p>
          <h2>Find the best destination for your travel style</h2>
        </div>
        <div className="hero-stat-grid">
          <div>
            <span>{dashboard?.total_destinations || 0}</span>
            <small>Destinations</small>
          </div>
          <div>
            <span>{dashboard?.average_rating || '0.0'}</span>
            <small>Avg Rating</small>
          </div>
          <div>
            <span>₹{dashboard?.average_cost ? Math.round(dashboard.average_cost) : 0}</span>
            <small>Avg Cost</small>
          </div>
        </div>
      </section>

      <main className="content-grid">
        <section id="traveler-preferences" className="panel form-panel">
          <h3>Traveler Preferences</h3>
          <form onSubmit={handleSubmit} className="travel-form">
            <label>
              Budget (INR)
              <input type="number" name="budget" value={form.budget} onChange={handleChange} />
            </label>
            <label>
              Number of days
              <input type="number" name="days" value={form.days} onChange={handleChange} />
            </label>
            <label>
              Travelers
              <input type="number" name="travelers" value={form.travelers} onChange={handleChange} />
            </label>
            <label>
              Travel type
              <select name="travel_type" value={form.travel_type} onChange={handleChange}>
                <option value="family">Family</option>
                <option value="friends">Friends</option>
                <option value="couple">Couple</option>
                <option value="solo">Solo</option>
                <option value="adventure">Adventure</option>
                <option value="luxury">Luxury</option>
              </select>
            </label>
            <label>
              Interests
              <input type="text" name="interests" value={form.interests} onChange={handleChange} />
            </label>
            <label>
              Preferred location
              <input type="text" name="location" value={form.location} onChange={handleChange} />
            </label>
            <label>
              Climate preference
              <select name="climate" value={form.climate} onChange={handleChange}>
                <option value="cool">Cool</option>
                <option value="warm">Warm</option>
                <option value="beach">Beach</option>
                <option value="mountain">Mountain</option>
                <option value="any">Any</option>
              </select>
            </label>
            <button className="primary-btn" type="submit" disabled={loading}>
              {loading ? 'Recommending...' : 'Get Recommendations'}
            </button>
          </form>
          {error && <div className="error-box">{error}</div>}
        </section>

        <section className="panel result-panel">
          <h3>Recommended Destinations</h3>
          <div className="recommendation-list">
            {recommendations.length === 0 ? (
              <p className="empty-state">Your recommendations will appear here after you submit the form.</p>
            ) : (
              recommendations.map((item) => (
                <div key={item.destination_id} className="recommend-card">
                  <div className="card-header">
                    <div>
                      <h4>{item.destination_name}</h4>
                      <small>{item.state}, {item.country}</small>
                    </div>
                    <span className="match-badge">{item.match_score}%</span>
                  </div>
                  <p className="cost-line">Estimated Cost: ₹{item.estimated_cost}</p>
                  <ul>
                    {item.reasons.map((reason) => (
                      <li key={reason}>{reason}</li>
                    ))}
                  </ul>
                </div>
              ))
            )}
          </div>
        </section>
      </main>

      <section className="panel map-panel">
        <div className="map-heading">
          <div>
            <p className="section-tag">Explore the region</p>
            <h3>Destination Map</h3>
          </div>
          <label className="map-picker">
            <span className="sr-only">Choose a destination to view on the map</span>
            <select
              value={selectedMapDestination?.destination_id || ''}
              onChange={(event) => {
                const selected = destinations.find(
                  (destination) => destination.destination_id === event.target.value,
                )
                setSelectedMapDestination(selected || null)
              }}
              disabled={destinations.length === 0}
            >
              {destinations.map((destination) => (
                <option key={destination.destination_id} value={destination.destination_id}>
                  {destination.destination_name}, {destination.country}
                </option>
              ))}
            </select>
          </label>
        </div>
        {selectedMapDestination ? (
          <>
            <iframe
              className="destination-map"
              title={`Map of ${selectedMapDestination.destination_name}`}
              src={`https://maps.google.com/maps?q=${encodeURIComponent(
                `${selectedMapDestination.destination_name}, ${selectedMapDestination.state}, ${selectedMapDestination.country}`,
              )}&output=embed`}
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
            />
            <a
              className="map-link"
              href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
                `${selectedMapDestination.destination_name}, ${selectedMapDestination.state}, ${selectedMapDestination.country}`,
              )}`}
              target="_blank"
              rel="noreferrer"
            >
              Open {selectedMapDestination.destination_name} in Google Maps
            </a>
          </>
        ) : (
          <p className="empty-state">Destination locations will appear here when loaded.</p>
        )}
      </section>

      <section className="analytics-grid">
        <div className="panel">
          <h3>Tourism Dashboard</h3>
          <div className="stats-row">
            <div className="stat-box">
              <span>{dashboard?.total_destinations || 0}</span>
              <small>Total Destinations</small>
            </div>
            <div className="stat-box">
              <span>{dashboard?.total_attractions || 0}</span>
              <small>Total Attractions</small>
            </div>
            <div className="stat-box">
              <span>₹{dashboard?.average_cost ? Math.round(dashboard.average_cost) : 0}</span>
              <small>Average Cost</small>
            </div>
          </div>

          <div className="chart-box">
            <h4>Popular Destinations</h4>
            <div className="chart-bars">
              {(dashboard?.popular_destinations || []).slice(0, 5).map((item) => (
                <div key={item.destination_id} className="bar-group">
                  <span>{item.destination_name}</span>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ height: `${item.popularity}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="panel">
          <h3>Budget Estimate</h3>
          {budgetEstimate ? (
            <div className="budget-card">
              <p><strong>{budgetEstimate.destination_name}</strong></p>
              <p>Minimum: ₹{budgetEstimate.minimum_cost}</p>
              <p>Average: ₹{budgetEstimate.average_cost}</p>
              <p>Maximum: ₹{budgetEstimate.maximum_cost}</p>
            </div>
          ) : (
            <p className="empty-state">Budget estimate will appear after submitting preferences.</p>
          )}

          <h3 className="plan-title">Travel Plan</h3>
          {travelPlan ? (
            <div className="plan-card">
              {travelPlan.daily_plan.map((item) => (
                <div className="day-plan" key={item.day}>
                  <h5>Day {item.day}</h5>
                  <p><strong>Morning:</strong> {item.morning}</p>
                  <p><strong>Afternoon:</strong> {item.afternoon}</p>
                  <p><strong>Evening:</strong> {item.evening}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-state">A generated itinerary will appear here.</p>
          )}
        </div>
      </section>

      <section className="panel destinations-panel">
        <h3>Available Destinations</h3>
        <div className="destination-grid">
          {(destinations || []).slice(0, 8).map((destination) => (
            <div className="mini-card" key={destination.destination_id}>
              <h4>{destination.destination_name}</h4>
              <p>{destination.category}</p>
              <small>{destination.state}</small>
              <div className="meta-row">
                <span>⭐ {destination.rating}</span>
                <span>₹{destination.average_cost}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

export default App
