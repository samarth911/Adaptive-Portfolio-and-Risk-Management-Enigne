export default function ActivityLog({ logs }) {
  return (
    <div className="card">
      <h2>Live Engine Activity</h2>

      <div className="log-container">
        {logs && logs.length > 0 ? (
          logs.slice().reverse().map((log, index) => (
            <div key={index} className="log-entry">
              <span className="log-time">{log.time}</span>
              <span className="log-message">{log.message}</span>
            </div>
          ))
        ) : (
          <p>No activity yet...</p>
        )}
      </div>
    </div>
  );
}
