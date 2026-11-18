import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { requestJson } from "./api";
const demoStations = [
  { station_id: "STN_YAM_01", station_name: "Yamuna · Old Railway Bridge", river: "Yamuna", state: "Delhi NCR", latitude: 28.6635, longitude: 77.2478, warning_level_m: 204.5, danger_level_m: 205.33, current_telemetry: { river_water_level_m: 205.15, water_level_rate_of_rise_m_hr: 0.08, rainfall_24h_mm: 84, rainfall_72h_mm: 172.5, soil_moisture_index: 0.88, upstream_discharge_cusecs: 245000, risk_level: 2, risk_label: "High" } },
  { station_id: "STN_YAM_02", station_name: "Yamuna · Okhla Barrage", river: "Yamuna", state: "Uttar Pradesh / Delhi", latitude: 28.5448, longitude: 77.3069, warning_level_m: 199.5, danger_level_m: 200.6, current_telemetry: { river_water_level_m: 199.85, water_level_rate_of_rise_m_hr: 0.05, rainfall_24h_mm: 62, rainfall_72h_mm: 135, soil_moisture_index: 0.82, upstream_discharge_cusecs: 210000, risk_level: 2, risk_label: "High" } },
  { station_id: "STN_HIN_01", station_name: "Hindon · Ghaziabad Barrage", river: "Hindon", state: "Uttar Pradesh", latitude: 28.6508, longitude: 77.4124, warning_level_m: 209, danger_level_m: 210.2, current_telemetry: { river_water_level_m: 208.2, water_level_rate_of_rise_m_hr: 0.02, rainfall_24h_mm: 28, rainfall_72h_mm: 65, soil_moisture_index: 0.6, upstream_discharge_cusecs: 35000, risk_level: 1, risk_label: "Medium" } },
  { station_id: "STN_HIN_02", station_name: "Hindon · Noida Sector 135", river: "Hindon", state: "Uttar Pradesh", latitude: 28.4985, longitude: 77.4012, warning_level_m: 196.2, danger_level_m: 197.5, current_telemetry: { river_water_level_m: 195.4, water_level_rate_of_rise_m_hr: 0.01, rainfall_24h_mm: 18, rainfall_72h_mm: 45, soil_moisture_index: 0.52, upstream_discharge_cusecs: 28000, risk_level: 0, risk_label: "Low" } }
];

const models = [
  { name: "XGBoost", score: 99.2, tag: "CHAMPION", color: "cyan" },
  { name: "Random Forest", score: 98.97, tag: "CANDIDATE", color: "violet" },
  { name: "Logistic Regression", score: 93.04, tag: "BASELINE", color: "slate" }
];

function RiskPill({ label }) {
  return <span className={`risk risk-${label.toLowerCase()}`}>{label}</span>;
}

function Icon({ children }) {
  return <span className="icon" aria-hidden="true">{children}</span>;
}

function App() {
  const [active, setActive] = useState("Overview");
  const [stations, setStations] = useState(demoStations);
  const [alerts, setAlerts] = useState([]);
  const [modelData, setModelData] = useState(null);
  const [selected, setSelected] = useState(demoStations[0]);
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([{ role: "assistant", text: "Good morning. I’m monitoring 6 stations across the NCR and upper Ganga basin. Ask me about risk, rainfall, or preparedness." }]);
  const [loadingChat, setLoadingChat] = useState(false);
  const [apiOnline, setApiOnline] = useState(false);
  const [loadingDashboard, setLoadingDashboard] = useState(true);
  const [dashboardError, setDashboardError] = useState("");
  const [dataMode, setDataMode] = useState("synthetic");

  useEffect(() => {
    Promise.all([
      requestJson("/api/stations"),
      requestJson("/api/alerts"),
      requestJson("/api/prediction/models")
    ])
      .then(([stationData, alertData, model]) => {
        setStations(stationData);
        setSelected(stationData[0]);
        setAlerts(alertData.alerts || []);
        setModelData(model);
        setDataMode(model.data_mode || "synthetic");
        setApiOnline(true);
      })
      .catch((error) => {
        setDashboardError(error.message);
        setDataMode("synthetic-offline");
      })
      .finally(() => setLoadingDashboard(false));
  }, []);

  const counts = useMemo(() => stations.reduce((acc, s) => {
    const level = s.current_telemetry.risk_level;
    acc[level] += 1;
    return acc;
  }, [0, 0, 0, 0]), [stations]);
  const highStations = stations.filter((s) => s.current_telemetry.risk_level >= 2);

  function sendMessage(event) {
    event.preventDefault();
    if (!query.trim() || loadingChat) return;
    const text = query.trim();
    setQuery("");
    setMessages((items) => [...items, { role: "user", text }]);
    setLoadingChat(true);
    requestJson("/api/agent/query", { method: "POST", body: JSON.stringify({ query: text }) })
      .then((data) => setMessages((items) => [...items, { role: "assistant", text: data.response || data.answer || "I could not complete that assessment. Please verify the telemetry manually.", trace: data.tool_trace }]))
      .catch((error) => setMessages((items) => [...items, { role: "assistant", text: `The agent service is unavailable (${error.message}). Based on current telemetry, prioritize the two High-risk Yamuna stations and verify the latest CWC bulletin.` }]))
      .finally(() => setLoadingChat(false));
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark">≈</div><div><strong>FLOOD<span>GUARD</span></strong><small>COMMAND CONSOLE</small></div></div>
        <div className="live-status"><span className={apiOnline ? "dot online" : "dot"} /> {apiOnline ? `API CONNECTED · ${dataMode.toUpperCase()}` : "OFFLINE · SYNTHETIC FALLBACK"}<span className="pulse" /></div>
        <nav>
          {["Overview", "Stations", "Model Lab", "AI Assistant"].map((item, index) => <button key={item} className={active === item ? "nav-item active" : "nav-item"} onClick={() => setActive(item)}><Icon>{["⌂", "⌖", "◈", "✦"][index]}</Icon>{item}{item === "Stations" && <em>{stations.length}</em>}</button>)}
        </nav>
        <div className="sidebar-footer"><div className="secure"><Icon>◉</Icon><div><b>SECURE SESSION</b><small>Operator: Field Command</small></div></div><div className="system-version">FLOODGUARD v1.0.0 <span>•</span> NCR REGION</div></div>
      </aside>
      <main className="main">
        <header className="topbar"><div><div className="eyebrow">NATIONAL FLOOD RESPONSE NETWORK <span>／</span> 18 NOV 2026 · 11:36 IST</div><h1>{active === "Overview" ? "Situation overview" : active}</h1></div><div className="top-actions"><button className="outline-btn"><span className="export-icon">⇩</span> Export report</button><button className="avatar">IM</button></div></header>
        {loadingDashboard && <div className="state-card card"><div className="spinner" /><strong>Loading FloodGuard telemetry…</strong><p>Connecting to the local decision-support service.</p></div>}
        {!loadingDashboard && dashboardError && <div className="data-banner warning"><strong>Offline demonstration mode</strong><span>{dashboardError}. Showing clearly labelled synthetic fallback telemetry.</span></div>}
        {!loadingDashboard && active === "Overview" && <Overview stations={stations} counts={counts} alerts={alerts} highStations={highStations} selected={selected} setSelected={setSelected} dataMode={dataMode} />}
        {!loadingDashboard && active === "Stations" && <Stations stations={stations} selected={selected} setSelected={setSelected} />}
        {!loadingDashboard && active === "Model Lab" && <ModelLab modelData={modelData} />}
        {active === "AI Assistant" && <Assistant messages={messages} query={query} setQuery={setQuery} sendMessage={sendMessage} loadingChat={loadingChat} />}
        <footer><span><span className={`dot ${apiOnline ? "online" : ""}`} /> {apiOnline ? "API CONNECTED" : "OFFLINE DEMONSTRATION MODE"}</span><span>{apiOnline ? "SYNTHETIC TELEMETRY · REFRESH ON RELOAD" : "BACKEND UNAVAILABLE · FALLBACK ACTIVE"} <b>↻</b></span></footer>
      </main>
    </div>
  );
}

function Overview({ stations, counts, alerts, highStations, selected, setSelected, dataMode }) {
  const t = selected.current_telemetry;
  const levelPercent = Math.min(100, Math.max(0, ((t.river_water_level_m - selected.warning_level_m + 0.7) / 1.53) * 100));
  return <div className="content"><div className="data-banner"><strong>{dataMode === "synthetic" ? "SYNTHETIC DATASET" : "OFFLINE SYNTHETIC FALLBACK"}</strong><span>For demonstration only · not an official emergency warning</span></div>
    <section className="metric-grid">
      <Metric label="MONITORED STATIONS" value={stations.length} detail="Across 3 river basins" icon="⌖" />
      <Metric label="ACTIVE ALERTS" value={alerts.length || highStations.length} detail="Requires attention" icon="!" tone="orange" />
      <Metric label="CRITICAL / HIGH" value={`${counts[3]} / ${counts[2]}`} detail="Risk-tier distribution" icon="⚠" tone="red" />
      <Metric label="SYSTEM CONFIDENCE" value="99.2%" detail="XGBoost champion model" icon="✦" tone="cyan" />
    </section>
    <section className="dashboard-grid">
      <div className="card map-card"><CardHeader title="REGIONAL RISK MAP" meta="LIVE TELEMETRY" /><div className="map"><div className="map-water water-one" /><div className="map-water water-two" /><div className="map-road road-one" /><div className="map-road road-two" /><div className="map-label label-delhi">DELHI NCR</div>{stations.map((s) => <button key={s.station_id} className={`map-pin pin-${s.current_telemetry.risk_label.toLowerCase()}`} style={{ left: `${((s.longitude - 77.1) / .8) * 100}%`, top: `${100 - ((s.latitude - 25) / 6) * 100}%` }} onClick={() => setSelected(s)} title={s.station_name}><span /></button>)}<div className="map-legend"><span><i className="legend-low" /> Low</span><span><i className="legend-medium" /> Medium</span><span><i className="legend-high" /> High</span><span><i className="legend-critical" /> Critical</span></div><div className="map-controls"><button>＋</button><button>−</button></div></div></div>
      <div className="card selected-card"><CardHeader title="SELECTED STATION" meta={selected.station_id} /><div className="station-title"><div className="river-avatar">≈</div><div><h2>{selected.station_name.replace(" · ", " — ")}</h2><p>{selected.river} river · {selected.state}</p></div><RiskPill label={t.risk_label} /></div><div className="gauge-row"><div className="gauge"><div className="gauge-inner"><strong>{t.river_water_level_m.toFixed(2)}<small>m</small></strong><span>Current level</span></div></div><div className="thresholds"><div><span className="threshold-mark warning" />Warning mark<strong>{selected.warning_level_m.toFixed(2)}m</strong></div><div><span className="threshold-mark danger" />Danger mark<strong>{selected.danger_level_m.toFixed(2)}m</strong></div><div><span className="trend-up">↑</span>Rate of rise<strong>{t.water_level_rate_of_rise_m_hr.toFixed(2)} m/hr</strong></div></div></div><div className="progress"><span style={{ width: `${levelPercent}%` }} /></div><div className="card-actions"><button className="text-btn">View station details <b>→</b></button><button className="icon-btn">⋮</button></div></div>
    </section>
    <section className="lower-grid"><div className="card telemetry-card"><CardHeader title="NETWORK TELEMETRY" meta="LAST 24 HOURS" /><div className="chart"><div className="chart-y"><span>205m</span><span>204m</span><span>203m</span><span>202m</span></div><svg viewBox="0 0 640 160" preserveAspectRatio="none"><defs><linearGradient id="fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor="#27c4dc" stopOpacity=".35" /><stop offset="1" stopColor="#27c4dc" stopOpacity="0" /></linearGradient></defs><path d="M0 125 C40 125 55 95 95 105 S150 120 185 88 S245 105 275 77 S320 96 355 62 S415 75 440 48 S480 74 510 51 S560 70 640 28 L640 160 L0 160Z" fill="url(#fill)" /><path d="M0 125 C40 125 55 95 95 105 S150 120 185 88 S245 105 275 77 S320 96 355 62 S415 75 440 48 S480 74 510 51 S560 70 640 28" fill="none" stroke="#27c4dc" strokeWidth="2.5" /><line x1="0" y1="77" x2="640" y2="77" stroke="#f59e0b" strokeDasharray="5 6" opacity=".8" /></svg><div className="chart-x"><span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span><span>NOW</span></div></div><div className="telemetry-stats"><Stat label="RAIN (24H)" value={`${t.rainfall_24h_mm} mm`} delta="+18.4%" up /><Stat label="SOIL SATURATION" value={`${Math.round(t.soil_moisture_index * 100)}%`} delta="Above normal" up /><Stat label="UPSTREAM FLOW" value={`${Math.round(t.upstream_discharge_cusecs / 1000)}k`} delta="cusecs" /></div></div>
      <div className="card alerts-card"><CardHeader title="ACTIVE ALERTS" meta={`${highStations.length} OPEN`} /><div className="alert-list">{highStations.slice(0, 3).map((s) => <div className="alert-item" key={s.station_id}><div className="alert-symbol">!</div><div><strong>{s.current_telemetry.risk_label.toUpperCase()} FLOOD WARNING</strong><p>{s.station_name} · Level {s.current_telemetry.river_water_level_m}m</p></div><span className="alert-time">NOW</span></div>)}{!highStations.length && <div className="empty">No active alerts in the network.</div>}</div><button className="view-all">View all alerts <b>→</b></button></div></section>
  </div>;
}

function Metric({ label, value, detail, icon, tone = "" }) { return <div className="metric card"><div className={`metric-icon ${tone}`}>{icon}</div><div><span>{label}</span><strong>{value}</strong><small>{detail}</small></div></div>; }
function CardHeader({ title, meta }) { return <div className="card-header"><h3>{title}</h3><span>{meta}</span></div>; }
function Stat({ label, value, delta, up }) { return <div><span>{label}</span><strong>{value}</strong><small className={up ? "positive" : ""}>{up && "↗ "}{delta}</small></div>; }

function Stations({ stations, selected, setSelected }) {
  return <div className="content"><div className="page-intro"><p>Live hydrological telemetry from every FloodGuard monitoring station.</p><button className="outline-btn">↻ Refresh data</button></div><div className="card table-card"><div className="table-toolbar"><div className="search">⌕ <input placeholder="Search stations or rivers" /></div><button className="filter-btn">Filter: All risks ▾</button></div><div className="table-wrap"><table><thead><tr><th>STATION</th><th>RIVER / REGION</th><th>WATER LEVEL</th><th>24H RAINFALL</th><th>RATE OF RISE</th><th>RISK</th><th /></tr></thead><tbody>{stations.map((s) => <tr key={s.station_id} onClick={() => setSelected(s)} className={selected.station_id === s.station_id ? "selected-row" : ""}><td><strong>{s.station_name}</strong><small>{s.station_id}</small></td><td>{s.river}<small>{s.state}</small></td><td><strong>{s.current_telemetry.river_water_level_m}m</strong><small>Danger {s.danger_level_m}m</small></td><td>{s.current_telemetry.rainfall_24h_mm} mm</td><td className={s.current_telemetry.water_level_rate_of_rise_m_hr > .04 ? "text-warn" : ""}>↑ {s.current_telemetry.water_level_rate_of_rise_m_hr} m/hr</td><td><RiskPill label={s.current_telemetry.risk_label} /></td><td>⋮</td></tr>)}</tbody></table></div></div></div>;
}

function ModelLab({ modelData }) {
  const report = modelData?.summary?.models;
  return <div className="content"><div className="page-intro"><p>Benchmarking the models that power FloodGuard risk classification.</p><span className="champion-note">✦ XGBoost is currently deployed as champion</span></div><div className="model-grid">{models.map((m) => { const data = report?.[m.name === "Random Forest" ? "RandomForest" : m.name === "Logistic Regression" ? "LogisticRegression" : "XGBoost"]; return <div className={`card model-card ${m.tag === "CHAMPION" ? "champion" : ""}`} key={m.name}><div className={`model-symbol ${m.color}`}>◈</div><div className="model-top"><div><h2>{m.name}</h2><span>{m.tag}</span></div>{m.tag === "CHAMPION" && <b>DEPLOYED</b>}</div><div className="model-score"><strong>{((data?.accuracy || m.score / 100) * 100).toFixed(2)}%</strong><span>accuracy</span></div><div className="model-bar"><i style={{ width: `${data?.accuracy ? data.accuracy * 100 : m.score}%` }} /></div><div className="model-details"><span>Weighted F1 <b>{data?.f1_score?.toFixed(4) || (m.score / 100).toFixed(4)}</b></span><span>Latency <b>{data?.training_time_sec || "—"}s</b></span></div></div> })}</div><div className="card feature-card"><CardHeader title="TOP PREDICTIVE SIGNALS" meta="XGBOOST FEATURE IMPORTANCE" /><div className="feature-list">{[["7-day rainfall accumulation", 91], ["Upstream discharge", 79], ["Stage / warning ratio", 54], ["72-hour rainfall", 43], ["Drainage strain index", 18]].map(([name, value]) => <div className="feature-row" key={name}><span>{name}</span><div><i style={{ width: `${value}%` }} /></div><b>{value}%</b></div>)}</div></div></div>;
}

function Assistant({ messages, query, setQuery, sendMessage, loadingChat }) { return <div className="content assistant-layout"><div className="card chat-card"><CardHeader title="FLOOD INTELLIGENCE ASSISTANT" meta="REACT AGENT · HUMAN OVERSIGHT" /><div className="chat-messages">{messages.map((m, i) => <div className={`message ${m.role}`} key={i}><div className="message-avatar">{m.role === "assistant" ? "✦" : "IM"}</div><div><span className="message-role">{m.role === "assistant" ? "FLOODGUARD AI" : "YOU"}</span><p>{m.text}</p>{m.trace && <button className="trace-btn">▸ View tool trace</button>}</div></div>)}{loadingChat && <div className="message assistant"><div className="message-avatar">✦</div><p className="typing">Analyzing telemetry <i /> <i /> <i /></p></div>}</div><form className="chat-input" onSubmit={sendMessage}><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Ask about flood risk, stations, or preparedness…" /><button>Send <b>↗</b></button></form></div><div className="card prompt-card"><h3>TRY ASKING</h3>{["Which stations need immediate attention?", "Summarize Yamuna risk factors", "What is the recommended response for High risk?"].map((q) => <button key={q} onClick={() => setQuery(q)}>{q}<span>→</span></button>)}<div className="safety-note"><b>◎ Human-in-the-loop</b><p>AI outputs are advisory. Verify all recommendations against official CWC and NDMA bulletins before action.</p></div></div></div>; }

createRoot(document.getElementById("root")).render(<App />);
