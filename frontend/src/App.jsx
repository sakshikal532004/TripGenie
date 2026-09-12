import { useState } from "react";
import "./App.css";

function App() {
  const [form, setForm] = useState({
    destination: "",
    duration_days: 3,
    travelers: 2,
    budget: 30000,
    interests: "",
  });

  const [loading, setLoading] = useState(false);
  const [trip, setTrip] = useState(null);
  const [error, setError] = useState("");

  // Feature pages
  const [activeFeature, setActiveFeature] = useState(null);

  // Ask TripGenie
  const [question, setQuestion] = useState("");
  const [questions, setQuestions] = useState([]);
  const [askLoading, setAskLoading] = useState(false);
  const [showPrevious, setShowPrevious] = useState(false);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const generateTrip = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setTrip(null);
    setQuestions([]);
    setShowPrevious(false);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/trips/plan",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            destination: form.destination,
            duration_days: Number(form.duration_days),
            travelers: Number(form.travelers),
            budget: Number(form.budget),
            interests: form.interests
              .split(",")
              .map((item) => item.trim())
              .filter(Boolean),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to generate trip"
        );
      }

      setTrip(data.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const askQuestion = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || !trip) {
      return;
    }

    setAskLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/trips/ask",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: trimmedQuestion,
            destination: trip.destination,
            duration_days: trip.duration_days,
            travelers: trip.travelers,
            budget: trip.estimated_total_cost,
            itinerary: trip.itinerary,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to get answer"
        );
      }

      setQuestions((previous) => [
        ...previous,
        {
          question: trimmedQuestion,
          answer: data.answer,
        },
      ]);

      setShowPrevious(false);
      setQuestion("");
    } catch (err) {
      setQuestions((previous) => [
        ...previous,
        {
          question: trimmedQuestion,
          answer:
            "Sorry, I couldn't answer that right now. Please try again.",
        },
      ]);

      setShowPrevious(false);
      setQuestion("");
    } finally {
      setAskLoading(false);
    }
  };

  const handleQuestionKeyDown = (e) => {
    if (e.key === "Enter" && !askLoading) {
      askQuestion();
    }
  };

  const featureData = {
    planning: {
      icon: "🤖",
      title: "AI Planning",
      subtitle: "Your personal AI travel planner",
      description:
        "TripGenie understands your destination, budget, travelers, and interests to create a personalized travel itinerary for you.",
      image:
        "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=1400&q=85",
      points: [
        "Personalized day-by-day itinerary",
        "Budget-aware travel planning",
        "Interest-based activities",
        "AI-powered recommendations",
      ],
      video:
        "https://www.youtube.com/embed/Scxs7L0vhZ4",
    },

    weather: {
      icon: "🌤️",
      title: "Live Weather",
      subtitle: "Plan your journey around the weather",
      description:
        "TripGenie can check current weather information for your destination and use it while planning your travel experience.",
      image:
        "https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=1400&q=85",
      points: [
        "Current weather information",
        "Destination-specific weather",
        "Better activity planning",
        "Weather-aware travel decisions",
      ],
      video:
        "https://www.youtube.com/embed/5qap5aO4i9A",
    },

    places: {
      icon: "📍",
      title: "Smart Places",
      subtitle: "Discover places worth visiting",
      description:
        "Tell TripGenie what you love and it can find attractions and places that match your travel interests.",
      image:
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1400&q=85",
      points: [
        "Interest-based attractions",
        "Real destination places",
        "Smart travel recommendations",
        "Activities for your itinerary",
      ],
      video:
        "https://www.youtube.com/embed/1La4QzGeaaQ",
    },
  };

  return (
    <div className="app">

      {/* Background animated orbs */}
      <div className="orb orb-one"></div>
      <div className="orb orb-two"></div>
      <div className="orb orb-three"></div>

      {/* ================= HEADER ================= */}

      <header className="hero">

        <div className="nav">

          <div className="logo">
            <span>✈</span> TripGenie
          </div>

          <div className="badge">
            ✨ AI Travel Agent
          </div>

        </div>

        <div className="hero-content">

          <div className="hero-text">

            <div className="eyebrow">
              ✨ SMART • PERSONALIZED • AI POWERED
            </div>

            <h1>
              Your next adventure,
              <span> planned by AI.</span>
            </h1>

            <p>
              Tell TripGenie where you want to go,
              what you love, and your budget.
              We'll build your personalized journey.
            </p>

            {/* ================= FEATURE BUTTONS ================= */}

            <div className="hero-features">

              <button
                type="button"
                className={`feature-pill ${
                  activeFeature === "planning"
                    ? "feature-active"
                    : ""
                }`}
                onClick={() =>
                  setActiveFeature("planning")
                }
              >
                <span>🤖</span>

                <div>
                  <strong>AI Planning</strong>
                  <small>Personalized trips</small>
                </div>
              </button>

              <button
                type="button"
                className={`feature-pill ${
                  activeFeature === "weather"
                    ? "feature-active"
                    : ""
                }`}
                onClick={() =>
                  setActiveFeature("weather")
                }
              >
                <span>🌤️</span>

                <div>
                  <strong>Live Weather</strong>
                  <small>Current conditions</small>
                </div>
              </button>

              <button
                type="button"
                className={`feature-pill ${
                  activeFeature === "places"
                    ? "feature-active"
                    : ""
                }`}
                onClick={() =>
                  setActiveFeature("places")
                }
              >
                <span>📍</span>

                <div>
                  <strong>Smart Places</strong>
                  <small>Discover attractions</small>
                </div>
              </button>

            </div>

          </div>

          <div className="floating-card">

            <div className="plane">
              ✈️
            </div>

            <div>
              <small>TRAVEL SMARTER</small>
              <strong>
                Explore the world 🌎
              </strong>
            </div>

          </div>

        </div>

      </header>

      {/* ================= FEATURE PAGE ================= */}

      {activeFeature && (
        <section className="feature-page">

          <button
            type="button"
            className="feature-back-btn"
            onClick={() => setActiveFeature(null)}
          >
            ← Back to Trip Planner
          </button>

          <div className="feature-page-content">

            <div className="feature-page-text">

              <div className="eyebrow">
                {featureData[activeFeature].icon}{" "}
                TRIPGENIE FEATURE
              </div>

              <h2>
                {featureData[activeFeature].title}
              </h2>

              <p>
                <strong>
                  {featureData[activeFeature].subtitle}
                </strong>
              </p>

              <p>
                {featureData[activeFeature].description}
              </p>

              <div className="feature-check-list">

                {featureData[activeFeature].points.map(
                  (point, index) => (
                    <div key={index}>
                      ✓ {point}
                    </div>
                  )
                )}

              </div>

              <button
                type="button"
                className="feature-action-btn"
                onClick={() => {
                  setActiveFeature(null);

                  setTimeout(() => {
                    document
                      .querySelector(".planner-card")
                      ?.scrollIntoView({
                        behavior: "smooth",
                      });
                  }, 100);
                }}
              >
                Start Planning ✨
              </button>

            </div>

            <div className="feature-page-image">

              <img
                src={featureData[activeFeature].image}
                alt={featureData[activeFeature].title}
              />

              <div className="image-glass-card">
                {featureData[activeFeature].icon}{" "}
                Powered by TripGenie AI
              </div>

            </div>

          </div>

          {/* Feature video */}

          <div className="feature-video-section">

            <div className="eyebrow">
              🎬 TRAVEL INSPIRATION
            </div>

            <h3>
              Get inspired for your next journey
            </h3>

            <div className="travel-video">

              <iframe
                src={featureData[activeFeature].video}
                title={`${featureData[activeFeature].title} travel video`}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              ></iframe>

            </div>

          </div>

        </section>
      )}

      {/* ================= MAIN ================= */}

      <main>

        {/* ================= PLANNER CARD ================= */}

        <section className="planner-card">

          <div className="section-heading">

            <div>
              <div className="eyebrow">
                ✨ CREATE YOUR JOURNEY
              </div>

              <h2>
                Where will you go?
              </h2>

              <p>
                Give us a few details and let
                TripGenie handle the planning.
              </p>
            </div>

          </div>

          <form onSubmit={generateTrip}>

            <div className="form-grid">

              {/* Destination */}

              <div className="form-group">

                <label>
                  Destination
                </label>

                <input
                  type="text"
                  name="destination"
                  value={form.destination}
                  onChange={handleChange}
                  placeholder="e.g. Goa, Dubai, Paris"
                  required
                />

              </div>

              {/* Duration */}

              <div className="form-group">

                <label>
                  Duration
                </label>

                <input
                  type="number"
                  name="duration_days"
                  min="1"
                  max="30"
                  value={form.duration_days}
                  onChange={handleChange}
                  required
                />

              </div>

              {/* Travelers */}

              <div className="form-group">

                <label>
                  Travelers
                </label>

                <input
                  type="number"
                  name="travelers"
                  min="1"
                  max="20"
                  value={form.travelers}
                  onChange={handleChange}
                  required
                />

              </div>

              {/* Budget */}

              <div className="form-group">

                <label>
                  Budget (₹)
                </label>

                <input
                  type="number"
                  name="budget"
                  min="1000"
                  value={form.budget}
                  onChange={handleChange}
                  required
                />

              </div>

            </div>

            {/* Interests */}

            <div className="form-group">

              <label>
                What are you interested in?
              </label>

              <input
                type="text"
                name="interests"
                value={form.interests}
                onChange={handleChange}
                placeholder="Beaches, food, adventure, shopping..."
              />

            </div>

            <button
              type="submit"
              className="generate-btn"
              disabled={loading}
            >
              {loading
                ? "✨ Creating your journey..."
                : "Generate My Trip ✨"}
            </button>

          </form>

          {error && (
            <div className="error-box">
              ⚠️ {error}
            </div>
          )}

        </section>
                {/* ================= TRIP RESULT ================= */}

        {trip && (
          <section className="result-section">

            <div className="result-header">

              <div>
                <div className="eyebrow">
                  ✨ YOUR AI GENERATED JOURNEY
                </div>

                <h2>
                  {trip.destination}
                </h2>

                <p>
                  {trip.duration_days} days •{" "}
                  {trip.travelers} travelers •{" "}
                  Budget ₹
                  {Number(
                    trip.estimated_total_cost
                  ).toLocaleString("en-IN")}
                </p>
              </div>

              <div className="result-badge">
                🤖 AI Planned
              </div>

            </div>

            {/* ================= TRIP SUMMARY ================= */}

            <div className="trip-summary">

              <div className="summary-card">
                <span>📍</span>
                <small>Destination</small>
                <strong>{trip.destination}</strong>
              </div>

              <div className="summary-card">
                <span>📅</span>
                <small>Duration</small>
                <strong>
                  {trip.duration_days} Days
                </strong>
              </div>

              <div className="summary-card">
                <span>👥</span>
                <small>Travelers</small>
                <strong>
                  {trip.travelers}
                </strong>
              </div>

              <div className="summary-card">
                <span>💰</span>
                <small>Total Budget</small>
                <strong>
                  ₹
                  {Number(
                    trip.estimated_total_cost
                  ).toLocaleString("en-IN")}
                </strong>
              </div>

            </div>

            {/* ================= ITINERARY ================= */}

            <div className="itinerary-section">

              <div className="section-heading">

                <div>
                  <div className="eyebrow">
                    🗺️ DAY BY DAY PLAN
                  </div>

                  <h3>
                    Your itinerary
                  </h3>

                  <p>
                    A personalized plan created
                    around your trip preferences.
                  </p>
                </div>

              </div>

              <div className="itinerary-list">

                {trip.itinerary?.map(
                  (day, index) => (
                    <div
                      className="day-card"
                      key={index}
                    >

                      <div className="day-header">

                        <div className="day-number">
                          {day.day}
                        </div>

                        <div>
                          <span>
                            DAY {day.day}
                          </span>

                          <h4>
                            Explore & Enjoy
                          </h4>
                        </div>

                      </div>

                      <div className="activity-list">

                        {day.activities?.map(
                          (activity, activityIndex) => (
                            <div
                              className="activity-card"
                              key={activityIndex}
                            >

                              <div className="activity-time">
                                {activity.time}
                              </div>

                              <div className="activity-content">

                                <strong>
                                  {activity.activity}
                                </strong>

                                <span>
                                  Estimated cost: ₹
                                  {Number(
                                    activity.estimated_cost || 0
                                  ).toLocaleString(
                                    "en-IN"
                                  )}
                                </span>

                              </div>

                            </div>
                          )
                        )}

                      </div>

                    </div>
                  )
                )}

              </div>

            </div>

            {/* ================= ASK TRIPGENIE ================= */}

            <div className="ask-tripgenie">

              <div className="ask-header">

                <div className="ask-icon">
                  ✨
                </div>

                <div>
                  <h3>
                    Ask TripGenie
                  </h3>

                  <p>
                    Have a question about this trip?
                  </p>
                </div>

              </div>

              {/* Suggestions */}

              <div className="suggestion-row">

                <button
                  type="button"
                  onClick={() =>
                    setQuestion(
                      "What should I pack for this trip?"
                    )
                  }
                >
                  🎒 What should I pack?
                </button>

                <button
                  type="button"
                  onClick={() =>
                    setQuestion(
                      "How can I save money on this trip?"
                    )
                  }
                >
                  💰 How can I save money?
                </button>

                <button
                  type="button"
                  onClick={() =>
                    setQuestion(
                      "What are the must-visit places?"
                    )
                  }
                >
                  📍 Must-visit places?
                </button>

              </div>

              {/* Question input */}

              <div className="question-box">

                <input
                  type="text"
                  value={question}
                  onChange={(e) =>
                    setQuestion(e.target.value)
                  }
                  onKeyDown={
                    handleQuestionKeyDown
                  }
                  placeholder="Ask anything about your trip..."
                />

                <button
                  type="button"
                  onClick={askQuestion}
                  disabled={
                    askLoading ||
                    !question.trim()
                  }
                >
                  {askLoading
                    ? "Thinking..."
                    : "Ask ✨"}
                </button>

              </div>

              {/* ================= QUESTION HISTORY ================= */}

              {questions.length > 0 && (
                <div className="question-history">

                  {/* Latest Question */}

                  <div className="question-item latest-question">

                    <div className="user-question">
                      You:{" "}
                      {
                        questions[
                          questions.length - 1
                        ].question
                      }
                    </div>

                    <div className="ai-answer">

                      <span>
                        ✨{" "}
                        {
                          questions[
                            questions.length - 1
                          ].answer
                        }
                      </span>

                      <button
                        type="button"
                        className="clear-answer-btn"
                        onClick={() => {
                          setQuestions([]);
                          setShowPrevious(false);
                        }}
                      >
                        Clear
                      </button>

                    </div>

                  </div>

                  {/* Previous Questions Button */}

                  {questions.length > 1 && (
                    <div className="previous-toggle">

                      <button
                        type="button"
                        onClick={() =>
                          setShowPrevious(
                            !showPrevious
                          )
                        }
                      >
                        {showPrevious
                          ? "▲ Hide Previous"
                          : `↺ View Previous (${
                              questions.length - 1
                            })`}
                      </button>

                    </div>
                  )}

                  {/* Previous Questions */}

                  {showPrevious &&
                    questions.length > 1 && (
                      <div className="previous-questions">

                        {[...questions]
                          .slice(0, -1)
                          .reverse()
                          .map(
                            (
                              item,
                              index
                            ) => (
                              <div
                                className="question-item previous-question"
                                key={index}
                              >

                                <div className="user-question">
                                  You:{" "}
                                  {item.question}
                                </div>

                                <div className="ai-answer">

                                  <span>
                                    ✨{" "}
                                    {item.answer}
                                  </span>

                                </div>

                              </div>
                            )
                          )}

                      </div>
                    )}

                </div>
              )}

            </div>

            {/* ================= TRAVEL INSPIRATION ================= */}

            <div className="travel-inspiration">

              <div className="inspiration-image">

                <img
                  src="https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=1600&q=85"
                  alt="Travel inspiration"
                />

                <div className="inspiration-overlay">

                  <span>🌎</span>

                  <div>
                    <small>
                      YOUR NEXT ADVENTURE
                    </small>

                    <strong>
                      The world is waiting for you.
                    </strong>
                  </div>

                </div>

              </div>

            </div>

            {/* ================= PRINT BUTTON ================= */}

            <div className="print-actions">

              <button
                type="button"
                className="print-btn"
                onClick={() => window.print()}
              >
                🖨️ Print Trip
              </button>

            </div>

          </section>
        )}

      </main>

      {/* ================= FOOTER ================= */}

      <footer>

        <div className="footer-logo">
          ✈ TripGenie
        </div>

        <p>
          AI-powered travel planning for your
          next adventure.
        </p>

        <div className="footer-line"></div>

        <small>
          Built with Python • LangGraph •
          LangChain • Groq • FastAPI •
          PostgreSQL • RAG • MCP
        </small>

      </footer>

    </div>
  );
}

export default App;