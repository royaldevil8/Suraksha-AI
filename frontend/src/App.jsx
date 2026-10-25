
import { useCallback, useEffect, useState } from 'react';

const API = 'http://127.0.0.1:8000/api';

const RESOURCE_LABELS = {
  ambulance: 'Ambulances',
  rescue_team: 'Rescue teams',
  boat: 'Boats',
  medical_kit: 'Medical kits',
  shelter_space: 'Shelter spaces',
};

function getMetrics(incidents) {
  return {
    incident_count: incidents.length,
    critical_count: incidents.filter(
      (i) => i.priority === 'CRITICAL'
    ).length,
    high_count: incidents.filter(
      (i) => i.priority === 'HIGH'
    ).length,
    duplicate_count: incidents.filter(
      (i) => Boolean(i.duplicate_of)
    ).length,
    conflict_count: incidents.filter(
      (i) => Boolean(i.conflict_flag)
    ).length,
    unverified_count: incidents.filter(
      (i) => i.evidence_status === 'unverified'
        || i.confidence < 0.6
    ).length,
    low_confidence_count: incidents.filter(
      (i) => i.confidence < 0.6
    ).length,
  };
}

function ResourceInventory({ resources, error }) {
  const inventory = resources?.inventory ?? [];
  const remaining = resources?.remaining ?? [];

  return (
    <section className="panel inventory-panel">
      <div className="panel-head">
        <div>
          <div className="eyebrow">RESOURCE AVAILABILITY</div>
          <h3>Resource inventory</h3>
        </div>
        <span className="count">
          {inventory.length} resource types
        </span>
      </div>

      {error && <div className="error">{error}</div>}

      {inventory.length === 0 ? (
        <p className="muted inventory-empty">
          Resource inventory is not available yet.
        </p>
      ) : (
        <div className="resource-grid">
          {inventory.map((item) => {
            const remainingItem = remaining.find(
              (resource) => resource.type === item.type
            );

            const available = Math.max(
              0,
              Math.min(item.count, remainingItem?.available ?? 0)
            );

            const allocated = Math.max(0, item.count - available);

            const percentage = item.count > 0
              ? (available / item.count) * 100
              : 0;

            const label =
              RESOURCE_LABELS[item.type]
              || item.type.replaceAll('_', ' ');

            return (
              <article
                className="resource-card"
                key={item.resource_id}
              >
                <div className="resource-card-head">
                  <span>{label}</span>
                  <span
                    className={
                      available === 0 ? 'stock-empty' : 'stock-ok'
                    }
                  >
                    {available === 0 ? 'Unavailable' : 'Available'}
                  </span>
                </div>

                <div className="resource-numbers">
                  <strong>{available}</strong>
                  <span>of {item.count} available</span>
                </div>

                <div
                  className="stock-track"
                  role="progressbar"
                  aria-label={`${label} available`}
                  aria-valuemin={0}
                  aria-valuemax={item.count}
                  aria-valuenow={available}
                >
                  <div
                    className={`stock-fill ${
                      available === 0 ? 'empty' : ''
                    }`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>

                <div className="stock-foot">
                  <span>{allocated} allocated/unavailable</span>
                  <span>{Math.round(percentage)}% left</span>
                </div>
              </article>
            );
          })}
        </div>
      )}

      <p className="muted inventory-note">
        Synthetic inventory for demonstration only. Availability does
        not confirm real-world emergency resources.
      </p>
    </section>
  );
}

function IncidentTable({ incidents }) {
  if (incidents.length === 0) {
    return (
      <div className="inventory-empty">
        No incidents available.
      </div>
    );
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Incident / Location</th>
            <th>Risk</th>
            <th>Evidence</th>
            <th>Recommended resources</th>
          </tr>
        </thead>

        <tbody>
          {incidents.slice(0, 30).map((incident) => {
            const priority = (
              incident.priority || 'LOW'
            ).toLowerCase();

            const confidence = Number(incident.confidence ?? 0);

            const evidenceLabel = incident.conflict_flag
              ? 'Conflict'
              : incident.duplicate_of
                ? 'Duplicate'
                : confidence < 0.6
                  ? 'Unverified'
                  : 'Review';

            const evidenceWarning =
              incident.conflict_flag
              || incident.duplicate_of
              || confidence < 0.6;

            const assignedResources =
              incident.assigned_resources ?? [];

            return (
              <tr key={incident.incident_id}>
                <td>
                  <b>{incident.incident_id}</b>
                  <div className="muted">
                    {incident.location_name || 'Unknown location'}
                    {' · '}
                    {(incident.incident_type || 'unknown')
                      .replaceAll('_', ' ')}
                  </div>
                  <div className="report">{incident.text}</div>
                </td>

                <td>
                  <span className={`priority ${priority}`}>
                    {incident.priority || 'LOW'}
                  </span>
                  <div className="risk">
                    {incident.risk_score ?? 0}/100
                  </div>
                </td>

                <td>
                  <span
                    className={`evidence ${
                      evidenceWarning ? 'warn' : ''
                    }`}
                  >
                    {evidenceLabel}
                  </span>
                  <div className="muted">
                    Confidence {(confidence * 100).toFixed(0)}%
                  </div>
                </td>

                <td>
                  {assignedResources.length > 0
                    ? assignedResources.map((resource, index) => (
                        <span
                          className="resource"
                          key={`${resource}-${index}`}
                        >
                          {String(resource).replaceAll('_', ' ')}
                        </span>
                      ))
                    : (
                      <span className="muted">
                        No stock assigned
                      </span>
                    )}

                  <details>
                    <summary>Why this score?</summary>
                    <ul>
                      {(incident.explanation ?? []).map(
                        (reason, index) => (
                          <li key={index}>{reason}</li>
                        )
                      )}
                    </ul>
                  </details>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {incidents.length > 30 && (
        <p className="muted table-note">
          Showing 30 of {incidents.length} incidents.
        </p>
      )}
    </div>
  );
}

export default function App() {
  const [summary, setSummary] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [resources, setResources] = useState({
    inventory: [],
    remaining: [],
  });

  const [error, setError] = useState('');
  const [resourceError, setResourceError] = useState('');
  const [loading, setLoading] = useState(true);
  const [replaying, setReplaying] = useState(false);

  const [text, setText] = useState(
    'Flood water rising fast near Rampur; 12 people trapped, urgent boat and rescue support needed.'
  );

  const [location, setLocation] = useState('Rampur');

  const refresh = useCallback(async () => {
    setLoading(true);

    try {
      const [summaryResponse, incidentsResponse, resourcesResponse] =
        await Promise.all([
          fetch(`${API}/summary`),
          fetch(`${API}/incidents`),
          fetch(`${API}/resources`),
        ]);

      if (!summaryResponse.ok || !incidentsResponse.ok) {
        throw new Error('Dashboard API request failed');
      }

      const [summaryData, incidentData] = await Promise.all([
        summaryResponse.json(),
        incidentsResponse.json(),
      ]);

      setSummary(summaryData);
      setIncidents(incidentData);
      setError('');

      if (resourcesResponse.ok) {
        setResources(await resourcesResponse.json());
        setResourceError('');
      } else {
        setResourceError('Resource API request failed. Retry refresh.');
      }
    } catch {
      setError(
        'Dashboard unavailable. Check that FastAPI is running at http://127.0.0.1:8000.'
      );
      setResourceError('Resource inventory could not be refreshed.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function replay(event) {
    event.preventDefault();

    const cleanText = text.trim();
    const cleanLocation = location.trim();

    if (!cleanText || !cleanLocation) {
      setError('Enter both a location and an incoming report.');
      return;
    }

    setReplaying(true);
    setError('');

    try {
      const response = await fetch(`${API}/scenario/replay`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: cleanText,
          location_name: cleanLocation,
          source: 'dashboard_scenario',
        }),
      });

      if (!response.ok) {
        throw new Error('Scenario replay request failed');
      }

      const snapshot = await response.json();
      const nextIncidents = snapshot.incidents ?? [];

      setIncidents(nextIncidents);

      setSummary((previous) => ({
        ...(previous ?? {}),
        report_count: snapshot.report_count,
        ...getMetrics(nextIncidents),
      }));

      // Scenario replay returns a separate synthetic snapshot.
      // Refresh resource availability from the regular resource endpoint.
      try {
        const resourceResponse = await fetch(`${API}/resources`);

        if (resourceResponse.ok) {
          setResources(await resourceResponse.json());
          setResourceError('');
        } else {
          setResourceError('Resource inventory could not be refreshed.');
        }
      } catch {
        setResourceError('Resource inventory could not be refreshed.');
      }
    } catch {
      setError(
        'Scenario replay failed. Check the backend and try again.'
      );
    } finally {
      setReplaying(false);
    }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brandmark">S</div>

        <div>
          <div className="eyebrow">DISASTER INTELLIGENCE PLATFORM</div>
          <h1>
            SURAKSHA <span>AI</span>
          </h1>
        </div>

        <div className="live">
          <i /> SYNTHETIC DEMO
        </div>
      </header>

      <section className="hero">
        <div>
          <div className="eyebrow">COMMAND OVERVIEW / AI-001</div>
          <h2>
            From fragmented reports
            <br />
            to actionable response.
          </h2>
          <p>
            Evidence-aware incident triage and constrained resource
            recommendations.
          </p>
        </div>

        <button
          className="ghost"
          onClick={refresh}
          disabled={loading || replaying}
        >
          {loading ? 'Refreshing…' : '↻ Refresh data'}
        </button>
      </section>

      {error && <div className="error" role="alert">{error}</div>}

      {loading && !summary && (
        <div className="panel inventory-empty" role="status">
          Loading dashboard data…
        </div>
      )}

      <section className="metrics">
        {[
          [
            'Reports processed',
            summary?.report_count ?? '—',
            'All synthetic sources',
          ],
          [
            'Critical incidents',
            summary?.critical_count ?? '—',
            'Highest current priority',
          ],
          [
            'Duplicates flagged',
            summary?.duplicate_count ?? '—',
            'Requires report review',
          ],
          [
            'Conflicts detected',
            summary?.conflict_count ?? '—',
            'Evidence is inconsistent',
          ],
        ].map(([label, value, note]) => (
          <article className="metric" key={label}>
            <div>{label}</div>
            <strong>{value}</strong>
            <small>{note}</small>
          </article>
        ))}
      </section>

      <ResourceInventory
        resources={resources}
        error={resourceError}
      />

      <section className="layout">
        <article className="panel incidents">
          <div className="panel-head">
            <div>
              <div className="eyebrow">PRIORITY QUEUE</div>
              <h3>Incident intelligence</h3>
            </div>
            <span className="count">
              {incidents.length} records
            </span>
          </div>

          <IncidentTable incidents={incidents} />
        </article>

        <aside className="panel replay">
          <div className="eyebrow">WHAT-IF SIMULATION</div>
          <h3>Scenario replay</h3>
          <p className="muted">
            Inject a new synthetic report and recompute the
            recommendation snapshot.
          </p>

          <form onSubmit={replay}>
            <label>
              Location
              <input
                value={location}
                onChange={(event) => setLocation(event.target.value)}
                maxLength={120}
                required
              />
            </label>

            <label>
              Incoming report
              <textarea
                rows="6"
                value={text}
                onChange={(event) => setText(event.target.value)}
                maxLength={5000}
                required
              />
            </label>

            <button
              className="primary"
              disabled={replaying || loading}
            >
              {replaying ? 'Replaying…' : 'Inject report & recompute'}
            </button>
          </form>

          <div className="notice">
            <b>Decision-support only</b>
            <br />
            Reports and locations are synthetic. Recommendations must
            be reviewed by a human operator; this prototype is not
            validated for real emergencies.
          </div>
        </aside>
      </section>

      <footer>
        SURAKSHA AI · Prototype v0.1 · Rule-based baseline · Human
        oversight required
      </footer>
    </main>
  );
}
