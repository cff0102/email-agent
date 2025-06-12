import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [emails, setEmails] = useState([]);
  const [meetings, setMeetings] = useState([]);
  const [userId, setUserId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [classification, setClassification] = useState({});

  const [activeMeeting, setActiveMeeting] = useState(null);
  const [meetingNotes, setMeetingNotes] = useState({});

  const handleMeetingClick = (idx) => {
    setActiveMeeting(activeMeeting === idx ? null : idx);
  };

  const handleNoteChange = (idx, value) => {
    setMeetingNotes((prev) => ({ ...prev, [idx]: value }));
  };

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get("user_id");
    if (id) {
      setUserId(id);
    }
  }, []);

  useEffect(() => {
    if (!userId) return;

    setLoading(true);
    const syncAndFetch = async () => {
      try {

        // Sync new emails and meetings into the database (must succeed to proceed)
        const syncRes = await fetch(`http://localhost:8000/emails/summary?user_id=${userId}`);
        if (!syncRes.ok) {
          const errText = await syncRes.text();
          throw new Error(`Sync error: ${syncRes.status} ${errText}`);
        }

        // Load stored emails (newest first)
        const emailsRes = await fetch(`http://localhost:8000/emails?user_id=${userId}`);
        const emailsData = await emailsRes.json();
        setEmails(emailsData.slice(0, 3));

        // Load stored meeting summaries
        const meetingsRes = await fetch(`http://localhost:8000/meetings?user_id=${userId}`);
        const meetingsData = await meetingsRes.json();
        setMeetings(meetingsData.map((m) => m.meeting_text));

        // Classify emails into new categories
        const classifyRes = await fetch(
          `http://localhost:8000/emails/classify?user_id=${userId}&limit=50`,
          { method: "POST" }
        );
        if (classifyRes.ok) {
          const classifyData = await classifyRes.json();
          setClassification(classifyData);
        } else {
          console.error("Failed to classify emails", await classifyRes.text());
        }
      } catch (err) {
        console.error("Failed to sync or fetch data", err);
      } finally {
        setLoading(false);
      }
    };

    syncAndFetch();
  }, [userId]);

  return (
    <div className="app">
      <header className="header">Your Email Dashboard</header>

      {!userId ? (
        <div className="login-section">
          <p>Please log in to view your dashboard.</p>
          <button
            className="login-button"
            onClick={() => {
              window.location.href = "http://localhost:8000/auth/login";
            }}
          >
            Sign in with Google
          </button>
        </div>
      ) : (
        <>
        <section className="meetings">
            <h2>Upcoming Meetings</h2>
            {loading ? (
              <p>Loading meetings...</p>
            ) : meetings.length === 0 ? (
              <p>No meetings found.</p>
            ) : (
              <ul className="meeting-list">
                {meetings.map((meeting, idx) => (
                  <li
                    key={idx}
                    className="email-card"
                    onClick={() => handleMeetingClick(idx)}
                  >
                    <p style={{ textAlign: 'left' }}>{meeting}</p>
                    {activeMeeting === idx && (
                      <textarea
                        className="meeting-notes"
                        placeholder="Add your notes..."
                        value={meetingNotes[idx] || ''}
                        onClick={(e) => e.stopPropagation()}
                        onChange={(e) => handleNoteChange(idx, e.target.value)}
                      />
                    )}
                  </li>
                ))}
              </ul>
            )}
          </section>

          {/* Classification sections for new categories */}
          <section className="categories">
            {['work','school','bills','travel','urgent','todos','other'].map((cat) => (
              <div key={cat} style={{ marginBottom: '1.5rem' }}>
                <h2 style={{ textAlign: 'center' }}>
                  {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </h2>
                {loading ? (
                  <p>Loading...</p>
                ) : (classification[cat] || []).length === 0 ? (
                  <p>No {cat} emails.</p>
                ) : (
                  (classification[cat] || []).map((item, idx) => (
                    <div className="email-card" key={idx}>
                      <p style={{ textAlign: 'left' }}>{item}</p>
                    </div>
                  ))
                )}
              </div>
            ))}
          </section>

          <section className="emails">
            <h2>Recent Emails</h2>
            {loading ? (
              <p>Loading emails...</p>
            ) : emails.length === 0 ? (
              <p>No emails found.</p>
            ) : (
              emails.map((email, idx) => (
                <div className="email-card" key={idx}>
                  <h3 style={{ textAlign: 'left' }}>
                    {email.subject || 'No Subject'}
                  </h3>
                  <p style={{ textAlign: 'left' }}>
                    <strong>From:</strong> {email.from || 'Unknown Sender'}
                  </p>
                  <p style={{ textAlign: 'left' }}>
                    <strong>Date:</strong>{' '}
                    {email.date
                      ? new Date(email.date).toLocaleString(undefined, {
                          dateStyle: 'medium',
                          timeStyle: 'short',
                        })
                      : 'No Date Provided'}
                  </p>
                  <p style={{ textAlign: 'left' }}>
                    {email.snippet || 'No content available.'}
                  </p>
                </div>
              ))
            )}
          </section>
        </>
      )}
    </div>
  );
}

export default App;
