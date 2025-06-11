import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [emails, setEmails] = useState([]);
  const [meetings, setMeetings] = useState([]);
  const [userId, setUserId] = useState(null);
  const [loading, setLoading] = useState(true);

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
    // If there's no userId yet (e.g. query param isn't set), exit early
    if (!userId) return;
  
    // Start loading before any network requests
    setLoading(true);
  
    const fetchSummary = async () => {
      try {
        setMeetings(["Meetings are loading..."])
        const res = await fetch(`http://localhost:8000/emails/summary?user_id=${userId}`);
        const data = await res.json();
        setMeetings(data.meetings || []);
      } catch (err) {
        console.error("Failed to fetch meetings", err);
      }
    };
  
    const fetchEmails = async () => {
      try {
        const res = await fetch(`http://localhost:8000/emails/recent?user_id=${userId}`);
        const data = await res.json();
        setEmails(data.slice(0, 3));
      } catch (err) {
        console.error("Failed to fetch emails", err);
      }
    };
  
    // Fetch both in parallel
    Promise.all([fetchSummary(), fetchEmails()])
      .finally(() => {
        // Stop loading after both are done (or if there's an error)
        setLoading(false);
      });
  }, [userId]);  //  Only re-run this block when userId changes

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
            {meetings.length === 0 ? (
              <p>No meetings found.</p>
            ) : (
              <ul className="meeting-list">
                {meetings.map((meeting, idx) => (
                  <li key={idx} className="email-card" onClick={() => handleMeetingClick(idx)}>
                    <p>{meeting}</p>
                    {activeMeeting === idx && (
                      <textarea
                        className="meeting-notes"
                        placeholder="Add your notes..."
                        value={meetingNotes[idx] || ""}
                        onClick={(e) => e.stopPropagation()}
                        onChange={(e) => handleNoteChange(idx, e.target.value)}
                      />
                    )}
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="emails">
            <h2>Recent Emails</h2>
            {emails.length === 0 ? (
              <p>Loading emails or none found.</p>
            ) : (
              emails.map((email, idx) => (
                <div className="email-card" key={idx}>
                  <h3>{email.subject || "No Subject"}</h3>
                  <p><strong>From:</strong> {email.from || "Unknown Sender"}</p>
                  <p><strong>Date:</strong> {email.date || "No Date Provided"}</p>
                  <p>{email.snippet || "No content available."}</p>
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
