import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import "./scenario.css";
import { requestJson } from "./api";
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
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
  const [messages, setMessages] = useState([{ role: "assistant", text: "### 👋 Hi — I’m your FloodGuard assistant\nI can check station risk, rainfall, river levels, flood history, affected regions, and preparedness actions.\nTry **“What can you do?”** or **“Is Delhi at risk?”**", synthesisSource: "offline-deterministic" }]);
  const [loadingChat, setLoadingChat] = useState(false);
  const [apiOnline, setApiOnline] = useState(false);
  const [loadingDashboard, setLoadingDashboard] = useState(true);
  const [dashboardError, setDashboardError] = useState("");
  const [dataMode, setDataMode] = useState("synthetic");
  const [incidents, setIncidents] = useState([]);
  const [chatSessionId, setChatSessionId] = useState("");

  async function loadDashboard(showLoader = false) {
    if (showLoader) setLoadingDashboard(true);
    try {
      const [stationData, alertData, model, incidentData] = await Promise.all([
        requestJson("/api/stations"),
        requestJson("/api/alerts"),
        requestJson("/api/prediction/models"),
        requestJson("/api/incidents")
      ]);
      setStations(stationData);
      setSelected((current) => stationData.find((station) => station.station_id === current?.station_id) || stationData[0]);
      setAlerts(alertData.alerts || []);
      setModelData(model);
      setIncidents(incidentData);
      setDataMode(model.data_mode || "synthetic");
      setApiOnline(true);
      setDashboardError("");
    } catch (error) {
      setDashboardError(error.message);
      setDataMode("synthetic-offline");
    } finally {
      setLoadingDashboard(false);
    }
  }

  useEffect(() => { loadDashboard(true); }, []);

  useEffect(() => {
    requestJson("/api/chat/sessions")
      .then(async (sessions) => {
        let session = sessions[0];
        if (!session) session = await requestJson("/api/chat/sessions", { method: "POST", body: JSON.stringify({ title: "FloodGuard operator chat" }) });
        setChatSessionId(session.id);
        const history = await requestJson(`/api/chat/sessions/${session.id}/messages`);
        if (history.messages?.length) {
          setMessages(history.messages.map((message) => ({ role: message.role, text: message.content, synthesisSource: message.synthesis_source, trace: [], plan: [] })));
        }
      })
      .catch(() => {});
  }, []);

  const counts = useMemo(() => stations.reduce((acc, s) => {
    const level = s.current_telemetry.risk_level;
    acc[level] += 1;
    return acc;
  }, [0, 0, 0, 0]), [stations]);
  const highStations = stations.filter((s) => s.current_telemetry.risk_level >= 2);

  function exportReport() {
    const rows = [
      ["station_id", "station_name", "river", "risk_level", "risk_label", "water_level_m", "warning_level_m", "danger_level_m", "rainfall_24h_mm", "source"],
      ...stations.map((station) => [
        station.station_id,
        station.station_name,
        station.river,
        station.current_telemetry.risk_level,
        station.current_telemetry.risk_label,
        station.current_telemetry.river_water_level_m,
        station.warning_level_m,
        station.danger_level_m,
        station.current_telemetry.rainfall_24h_mm,
        dataMode
      ])
    ];
    const csv = rows.map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(",")).join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = `floodguard-${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  async function ensureChatSession() {
    if (chatSessionId) return chatSessionId;
    const sessions = await requestJson("/api/chat/sessions");
    const session = sessions[0] || await requestJson("/api/chat/sessions", { method: "POST", body: JSON.stringify({ title: "FloodGuard operator chat" }) });
    setChatSessionId(session.id);
    return session.id;
  }

  async function sendMessage(event) {
    event.preventDefault();
    if (!query.trim() || loadingChat) return;
    const text = query.trim();
    setQuery("");
    setMessages((items) => [...items, { role: "user", text }]);
    setLoadingChat(true);
    try {
      const sessionId = await ensureChatSession();
      await requestJson(`/api/chat/sessions/${sessionId}/messages`, { method: "POST", body: JSON.stringify({ role: "user", content: text, synthesis_source: "operator-input", tool_count: 0 }) });
      const data = await requestJson("/api/agent/query", { method: "POST", body: JSON.stringify({ query: text }) });
      const assistantMessage = {
        role: "assistant",
        text: data.response || data.answer || "I could not complete that assessment. Please verify the telemetry manually.",
        trace: data.tool_calls || data.tool_trace || [],
        plan: data.plan || [],
        synthesisSource: data.synthesis_source || "offline-deterministic",
      };
      setMessages((items) => [...items, assistantMessage]);
      await requestJson(`/api/chat/sessions/${sessionId}/messages`, { method: "POST", body: JSON.stringify({ role: "assistant", content: assistantMessage.text, synthesis_source: assistantMessage.synthesisSource, tool_count: assistantMessage.trace.length }) });
    } catch (error) {
      setMessages((items) => [...items, { role: "assistant", text: `The agent service is unavailable (${error.message}). Based on current telemetry, prioritize the two High-risk Yamuna stations and verify the latest CWC bulletin.` }]);
    } finally {
      setLoadingChat(false);
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark">≈</div><div><strong>FLOOD<span>GUARD</span></strong><small>COMMAND CONSOLE</small></div></div>
        <div className="live-status"><span className={apiOnline ? "dot online" : "dot"} /> {apiOnline ? `API CONNECTED · ${dataMode.toUpperCase()}` : "OFFLINE · SYNTHETIC FALLBACK"}<span className="pulse" /></div>
        <nav>
          {["Overview", "Stations", "Model Lab", "Scenario Lab", "Incidents", "AI Assistant"].map((item, index) => <button key={item} className={active === item ? "nav-item active" : "nav-item"} onClick={() => setActive(item)}><Icon>{["⌂", "⌖", "◈", "⚗", "◎", "✦"][index]}</Icon>{item}{item === "Stations" && <em>{stations.length}</em>}</button>)}
        </nav>
        <div className="sidebar-footer"><div className="secure"><Icon>◉</Icon><div><b>SECURE SESSION</b><small>Operator: Field Command</small></div></div><div className="system-version">FLOODGUARD v1.0.0 <span>•</span> NCR REGION</div></div>
      </aside>
      <main className="main">
        <header className="topbar"><div><div className="eyebrow">NATIONAL FLOOD RESPONSE NETWORK <span>／</span> 18 NOV 2026 · 11:36 IST</div><h1>{active === "Overview" ? "Situation overview" : active}</h1></div><div className="top-actions"><button className="outline-btn" onClick={exportReport}><span className="export-icon">⇩</span> Export report</button><button className="avatar">IM</button></div></header>
        {!loadingDashboard && <button className="floating-refresh" onClick={() => loadDashboard(true)} title="Refresh synthetic telemetry">↻ Refresh</button>}
        {loadingDashboard && <div className="state-card card"><div className="spinner" /><strong>Loading FloodGuard telemetry…</strong><p>Connecting to the local decision-support service.</p></div>}
        {!loadingDashboard && dashboardError && <div className="data-banner warning"><strong>Offline demonstration mode</strong><span>{dashboardError}. Showing clearly labelled synthetic fallback telemetry.</span></div>}
        {!loadingDashboard && active === "Overview" && <Overview stations={stations} counts={counts} alerts={alerts} highStations={highStations} selected={selected} setSelected={setSelected} setActive={setActive} dataMode={dataMode} />}
        {!loadingDashboard && active === "Stations" && <Stations stations={stations} selected={selected} setSelected={setSelected} />}
        {!loadingDashboard && active === "Model Lab" && <ModelLab modelData={modelData} />}
        {!loadingDashboard && active === "Scenario Lab" && <ScenarioLab stations={stations} />}
        {!loadingDashboard && active === "Incidents" && <Incidents incidents={incidents} setIncidents={setIncidents} stations={stations} />}
        {active === "AI Assistant" && <Assistant messages={messages} query={query} setQuery={setQuery} sendMessage={sendMessage} loadingChat={loadingChat} />}
        <footer><span><span className={`dot ${apiOnline ? "online" : ""}`} /> {apiOnline ? "API CONNECTED" : "OFFLINE DEMONSTRATION MODE"}</span><span>{apiOnline ? "SYNTHETIC TELEMETRY · REFRESH ON RELOAD" : "BACKEND UNAVAILABLE · FALLBACK ACTIVE"} <b>↻</b></span></footer>
      </main>
    </div>
  );
}

function MapFocus({ station }) {
  const map = useMap();
  useEffect(() => {
    if (station) map.setView([station.latitude, station.longitude], 8, { animate: true });
  }, [station, map]);
  return null;
}

function Overview({ stations, counts, alerts, highStations, selected, setSelected, setActive, dataMode }) {
  const t = selected.current_telemetry;
  const levelPercent = Math.min(100, Math.max(0, ((t.river_water_level_m - selected.warning_level_m + 0.7) / 1.53) * 100));
  const [riskFilter, setRiskFilter] = useState("All");
  const [alertFilter, setAlertFilter] = useState("All");
  const [networkSeries, setNetworkSeries] = useState([]);
  const [networkSeriesError, setNetworkSeriesError] = useState("");
  useEffect(() => {
    requestJson("/api/stations/network/history")
      .then((data) => setNetworkSeries(data.series || []))
      .catch((error) => setNetworkSeriesError(error.message));
  }, []);
  const visibleStations = riskFilter === "All" ? stations : stations.filter((station) => station.current_telemetry.risk_label === riskFilter);
  const visibleAlerts = alertFilter === "All" ? highStations : highStations.filter((station) => station.current_telemetry.risk_label === alertFilter);
  const networkLevels = networkSeries.map((point) => point.average_water_level_m);
  const networkMin = networkLevels.length ? Math.min(...networkLevels) : 0;
  const networkMax = networkLevels.length ? Math.max(...networkLevels) : 1;
  const networkPadding = Math.max((networkMax - networkMin) * 0.18, 0.05);
  const chartMin = networkMin - networkPadding;
  const chartMax = networkMax + networkPadding;
  const networkPoints = networkSeries.map((point, index) => {
    const x = networkSeries.length > 1 ? (index / (networkSeries.length - 1)) * 640 : 0;
    const y = 130 - ((point.average_water_level_m - chartMin) / Math.max(chartMax - chartMin, 0.01)) * 105;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
  const chartArea = networkPoints ? `M0 160 L${networkPoints.replaceAll(" ", " L")} L640 160 Z` : "";
  const chartLine = networkPoints ? `M${networkPoints.replaceAll(" ", " L")}` : "";
  const chartLabels = networkLevels.length
    ? [chartMax, chartMax - (chartMax - chartMin) / 3, chartMax - (chartMax - chartMin) * 2 / 3, chartMin]
    : [0, 0, 0, 0];
  return <div className="content"><div className="data-banner"><strong>{dataMode === "synthetic" ? "SYNTHETIC DATASET" : "OFFLINE SYNTHETIC FALLBACK"}</strong><span>For demonstration only · not an official emergency warning</span></div>
    <section className="metric-grid">
      <Metric label="MONITORED STATIONS" value={stations.length} detail="Across 3 river basins" icon="⌖" />
      <Metric label="ACTIVE ALERTS" value={alerts.length || highStations.length} detail="Requires attention" icon="!" tone="orange" />
      <Metric label="CRITICAL / HIGH" value={`${counts[3]} / ${counts[2]}`} detail="Risk-tier distribution" icon="⚠" tone="red" />
      <Metric label="SYSTEM CONFIDENCE" value="99.2%" detail="XGBoost champion model" icon="✦" tone="cyan" />
    </section>
    <section className="dashboard-grid">
      <div className="card map-card"><CardHeader title="REGIONAL RISK MAP" meta="LIVE TELEMETRY" /><div className="map-toolbar"><label>Risk filter<select value={riskFilter} onChange={(event) => setRiskFilter(event.target.value)}><option>All</option><option>Low</option><option>Medium</option><option>High</option><option>Critical</option></select></label><span>{visibleStations.length} of {stations.length} stations</span></div><div className="operational-map"><MapContainer center={[27.8, 78.5]} zoom={6} scrollWheelZoom={true} attributionControl={false}><TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" attribution="&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors &copy; <a href='https://carto.com/attributions'>CARTO</a>" /><MapFocus station={selected} />{visibleStations.map((station) => { const risk = station.current_telemetry.risk_label.toLowerCase(); const colors = { low: "#36cb96", medium: "#efbb43", high: "#f5a623", critical: "#f06456" }; return <CircleMarker key={station.station_id} center={[station.latitude, station.longitude]} radius={10} pathOptions={{ color: colors[risk], fillColor: colors[risk], fillOpacity: .9, weight: 3 }} eventHandlers={{ click: () => setSelected(station) }}><Popup><strong>{station.station_name}</strong><br />Risk: {station.current_telemetry.risk_label}<br />Level: {station.current_telemetry.river_water_level_m} m</Popup></CircleMarker>; })}</MapContainer></div><div className="map-legend"><span><i className="legend-low" /> Low</span><span><i className="legend-medium" /> Medium</span><span><i className="legend-high" /> High</span><span><i className="legend-critical" /> Critical</span></div></div>
      <div className="card selected-card"><CardHeader title="SELECTED STATION" meta={selected.station_id} /><div className="station-title"><div className="river-avatar">≈</div><div><h2>{selected.station_name.replace(" · ", " — ")}</h2><p>{selected.river} river · {selected.state}</p></div><RiskPill label={t.risk_label} /></div><div className="gauge-row"><div className="gauge"><div className="gauge-inner"><strong>{t.river_water_level_m.toFixed(2)}<small>m</small></strong><span>Current level</span></div></div><div className="thresholds"><div><span className="threshold-mark warning" />Warning mark<strong>{selected.warning_level_m.toFixed(2)}m</strong></div><div><span className="threshold-mark danger" />Danger mark<strong>{selected.danger_level_m.toFixed(2)}m</strong></div><div><span className="trend-up">↑</span>Rate of rise<strong>{t.water_level_rate_of_rise_m_hr.toFixed(2)} m/hr</strong></div></div></div><div className="progress"><span style={{ width: `${levelPercent}%` }} /></div><div className="card-actions"><button className="text-btn" onClick={() => setActive("Stations")}>View station details <b>→</b></button><button className="icon-btn">⋮</button></div></div>
    </section>
    <section className="lower-grid"><div className="card telemetry-card"><CardHeader title="NETWORK TELEMETRY" meta={networkSeriesError ? "HISTORY UNAVAILABLE" : "24H SYNTHETIC SERIES"} /><div className="chart"><div className="chart-y">{chartLabels.map((label, index) => <span key={index}>{label.toFixed(1)}m</span>)}</div><svg viewBox="0 0 640 160" preserveAspectRatio="none"><defs><linearGradient id="fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor="#27c4dc" stopOpacity=".35" /><stop offset="1" stopColor="#27c4dc" stopOpacity="0" /></linearGradient></defs>{networkSeriesError ? <text x="320" y="80" textAnchor="middle" fill="#7899a4" fontSize="12">Network history unavailable</text> : <>{chartArea && <><path d={chartArea} fill="url(#fill)" /><path d={chartLine} fill="none" stroke="#27c4dc" strokeWidth="2.5" /></>}</>}</svg><div className="chart-x"><span>-24h</span><span>-18h</span><span>-12h</span><span>-6h</span><span>NOW</span></div></div><div className="telemetry-stats"><Stat label="RAIN (24H)" value={`${t.rainfall_24h_mm} mm`} delta="+18.4%" up /><Stat label="SOIL SATURATION" value={`${Math.round(t.soil_moisture_index * 100)}%`} delta="Above normal" up /><Stat label="UPSTREAM FLOW" value={`${Math.round(t.upstream_discharge_cusecs / 1000)}k`} delta="cusecs" /></div></div>
      <div className="card alerts-card"><CardHeader title="ACTIVE ALERTS" meta={`${visibleAlerts.length} SHOWN`} /><div className="alert-toolbar"><label>Severity<select value={alertFilter} onChange={(event) => setAlertFilter(event.target.value)}><option>All</option><option>High</option><option>Critical</option></select></label></div><div className="alert-list">{visibleAlerts.slice(0, 3).map((s) => <div className="alert-item" key={s.station_id}><div className="alert-symbol">!</div><div><strong>{s.current_telemetry.risk_label.toUpperCase()} FLOOD WARNING</strong><p>{s.station_name} · Level {s.current_telemetry.river_water_level_m}m</p></div><span className="alert-time">NOW</span></div>)}{!visibleAlerts.length && <div className="empty">No active alerts match this filter.</div>}</div><button className="view-all" onClick={() => setActive("Stations")}>View all stations <b>→</b></button></div></section>
  </div>;
}

function Metric({ label, value, detail, icon, tone = "" }) { return <div className="metric card"><div className={`metric-icon ${tone}`}>{icon}</div><div><span>{label}</span><strong>{value}</strong><small>{detail}</small></div></div>; }
function CardHeader({ title, meta }) { return <div className="card-header"><h3>{title}</h3><span>{meta}</span></div>; }
function Stat({ label, value, delta, up }) { return <div><span>{label}</span><strong>{value}</strong><small className={up ? "positive" : ""}>{up && "↗ "}{delta}</small></div>; }

function Stations({ stations, selected, setSelected }) {
  const [search, setSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState("All");
  const filtered = stations.filter((station) => {
    const matchesSearch = `${station.station_name} ${station.river} ${station.state} ${station.station_id}`.toLowerCase().includes(search.toLowerCase());
    const matchesRisk = riskFilter === "All" || station.current_telemetry.risk_label === riskFilter;
    return matchesSearch && matchesRisk;
  });
  const telemetry = selected.current_telemetry;
  const [history, setHistory] = useState([]);
  const [historyError, setHistoryError] = useState("");

  useEffect(() => {
    setHistory([]);
    setHistoryError("");
    requestJson(`/api/stations/${selected.station_id}/history`)
      .then((data) => setHistory(data.series || []))
      .catch((error) => setHistoryError(error.message));
  }, [selected.station_id]);

  const historyPoints = history.length > 1
    ? history.map((point, index) => {
        const x = (index / (history.length - 1)) * 300;
        const levels = history.map((item) => item.river_water_level_m);
        const min = Math.min(...levels);
        const max = Math.max(...levels);
        const y = 74 - ((point.river_water_level_m - min) / Math.max(max - min, 0.01)) * 58;
        return `${x},${y}`;
      }).join(" ")
    : "";

  return <div className="content"><div className="page-intro"><p>Synthetic hydrological telemetry from every FloodGuard monitoring station.</p><span className="champion-note">{filtered.length} of {stations.length} stations displayed</span></div><div className="station-layout"><div className="card table-card"><div className="table-toolbar"><div className="search">⌕ <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search stations, rivers, or regions" /></div><select className="filter-btn" value={riskFilter} onChange={(event) => setRiskFilter(event.target.value)}><option>All</option><option>Low</option><option>Medium</option><option>High</option><option>Critical</option></select></div><div className="table-wrap"><table><thead><tr><th>STATION</th><th>RIVER / REGION</th><th>WATER LEVEL</th><th>24H RAIN</th><th>RATE OF RISE</th><th>RISK</th></tr></thead><tbody>{filtered.map((station) => <tr key={station.station_id} onClick={() => setSelected(station)} className={selected.station_id === station.station_id ? "selected-row" : ""}><td><strong>{station.station_name}</strong><small>{station.station_id}</small></td><td>{station.river}<small>{station.state}</small></td><td><strong>{station.current_telemetry.river_water_level_m}m</strong><small>Danger {station.danger_level_m}m</small></td><td>{station.current_telemetry.rainfall_24h_mm} mm</td><td className={station.current_telemetry.water_level_rate_of_rise_m_hr > .04 ? "text-warn" : ""}>↑ {station.current_telemetry.water_level_rate_of_rise_m_hr} m/hr</td><td><RiskPill label={station.current_telemetry.risk_label} /></td></tr>)}</tbody></table>{filtered.length === 0 && <div className="empty-table">No stations match the current search and risk filter.</div>}</div></div><div className="card station-detail"><CardHeader title="STATION DETAIL" meta={selected.station_id} /><div className="station-detail-title"><div className="river-avatar">≈</div><div><h2>{selected.station_name}</h2><p>{selected.river} · {selected.state}</p></div><RiskPill label={telemetry.risk_label} /></div><dl className="detail-grid"><div><dt>Coordinates</dt><dd>{selected.latitude}, {selected.longitude}</dd></div><div><dt>Elevation</dt><dd>{selected.elevation_m} m</dd></div><div><dt>Warning mark</dt><dd>{selected.warning_level_m} m</dd></div><div><dt>Danger mark</dt><dd>{selected.danger_level_m} m</dd></div><div><dt>Water level</dt><dd>{telemetry.river_water_level_m} m</dd></div><div><dt>Rise rate</dt><dd>{telemetry.water_level_rate_of_rise_m_hr} m/hr</dd></div><div><dt>24h rainfall</dt><dd>{telemetry.rainfall_24h_mm} mm</dd></div><div><dt>72h rainfall</dt><dd>{telemetry.rainfall_72h_mm} mm</dd></div><div><dt>Soil saturation</dt><dd>{Math.round(telemetry.soil_moisture_index * 100)}%</dd></div><div><dt>Upstream discharge</dt><dd>{telemetry.upstream_discharge_cusecs.toLocaleString()} cusecs</dd></div>  </dl><div className="detail-history"><b>24-hour synthetic water level</b>{historyError ? <p>{historyError}</p> : history.length > 0 ? <svg className="history-sparkline" viewBox="0 0 300 82" preserveAspectRatio="none"><defs><linearGradient id="historyFill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor="#2ac3d8" stopOpacity=".32" /><stop offset="1" stopColor="#2ac3d8" stopOpacity="0" /></linearGradient></defs><polygon points={`0,82 ${historyPoints} 300,82`} fill="url(#historyFill)" /><polyline points={historyPoints} fill="none" stroke="#2ac3d8" strokeWidth="2.5" /></svg> : <p>Loading synthetic history…</p>}<p>This series is generated for demonstration and is not real observed history.</p></div></div></div></div>;}

function ModelLab({ modelData }) {
  const report = modelData?.summary?.models;
  return <div className="content"><div className="page-intro"><p>Benchmarking the models that power FloodGuard risk classification.</p><span className="champion-note">✦ XGBoost is currently deployed as champion</span></div><div className="model-grid">{models.map((m) => { const data = report?.[m.name === "Random Forest" ? "RandomForest" : m.name === "Logistic Regression" ? "LogisticRegression" : "XGBoost"]; return <div className={`card model-card ${m.tag === "CHAMPION" ? "champion" : ""}`} key={m.name}><div className={`model-symbol ${m.color}`}>◈</div><div className="model-top"><div><h2>{m.name}</h2><span>{m.tag}</span></div>{m.tag === "CHAMPION" && <b>DEPLOYED</b>}</div><div className="model-score"><strong>{((data?.accuracy || m.score / 100) * 100).toFixed(2)}%</strong><span>accuracy</span></div><div className="model-bar"><i style={{ width: `${data?.accuracy ? data.accuracy * 100 : m.score}%` }} /></div><div className="model-details"><span>Weighted F1 <b>{data?.f1_score?.toFixed(4) || (m.score / 100).toFixed(4)}</b></span><span>Latency <b>{data?.training_time_sec || "—"}s</b></span></div></div> })}</div><div className="card feature-card"><CardHeader title="TOP PREDICTIVE SIGNALS" meta="XGBOOST FEATURE IMPORTANCE" /><div className="feature-list">{[["7-day rainfall accumulation", 91], ["Upstream discharge", 79], ["Stage / warning ratio", 54], ["72-hour rainfall", 43], ["Drainage strain index", 18]].map(([name, value]) => <div className="feature-row" key={name}><span>{name}</span><div><i style={{ width: `${value}%` }} /></div><b>{value}%</b></div>)}</div></div></div>;
}

function ScenarioLab({ stations }) {
  const [stationId, setStationId] = useState(stations[0]?.station_id || "");
  const station = stations.find((item) => item.station_id === stationId) || stations[0];
  const telemetry = station?.current_telemetry;
  const makeValues = (item) => ({
    rainfall_1h_mm: item.current_telemetry.rainfall_1h_mm,
    rainfall_24h_mm: item.current_telemetry.rainfall_24h_mm,
    rainfall_72h_mm: item.current_telemetry.rainfall_72h_mm,
    rainfall_7d_mm: item.current_telemetry.rainfall_7d_mm,
    river_water_level_m: item.current_telemetry.river_water_level_m,
    water_level_rate_of_rise_m_hr: item.current_telemetry.water_level_rate_of_rise_m_hr,
    soil_moisture_index: item.current_telemetry.soil_moisture_index,
    upstream_discharge_cusecs: item.current_telemetry.upstream_discharge_cusecs,
    temperature_c: item.current_telemetry.temperature_c,
    humidity_pct: item.current_telemetry.humidity_pct,
  });
  const [values, setValues] = useState(() => station ? makeValues(station) : {});
  const [baseline, setBaseline] = useState(null);
  const [scenario, setScenario] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [weatherStatus, setWeatherStatus] = useState("");
  const [recentRuns, setRecentRuns] = useState(() => {
    try { return JSON.parse(localStorage.getItem("floodguard-scenario-runs") || "[]"); }
    catch { return []; }
  });

  useEffect(() => {
    if (station) {
      setValues(makeValues(station));
      setBaseline(null);
      setScenario(null);
      setError("");
    }
  }, [stationId]);

  async function runComparison() {
    setLoading(true);
    setError("");
    try {
      const base = await requestJson("/api/prediction/predict", { method: "POST", body: JSON.stringify({ location: station.station_name }) });
      const simulated = await requestJson("/api/prediction/predict", { method: "POST", body: JSON.stringify({ location: station.station_name, feature_override: values }) });
      setBaseline(base);
      setScenario(simulated);
      const run = {
        id: `${Date.now()}`,
        created_at: new Date().toISOString(),
        station_id: station.station_id,
        station_name: station.station_name,
        baseline_risk: base.predicted_risk_label,
        baseline_confidence: base.confidence,
        simulated_risk: simulated.predicted_risk_label,
        simulated_confidence: simulated.confidence,
        tier_change: simulated.predicted_risk_level - base.predicted_risk_level,
        feature_overrides: values,
        data_mode: simulated.data_mode,
        model_version: simulated.model_version,
      };
      setRecentRuns((current) => {
        const updated = [run, ...current].slice(0, 10);
        localStorage.setItem("floodguard-scenario-runs", JSON.stringify(updated));
        return updated;
      });
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadLiveWeather() {
    setWeatherLoading(true);
    setWeatherStatus("");
    setError("");
    try {
      const result = await requestJson(`/api/integrations/weather/${stationId}`);
      const weather = result.weather;
      setValues((current) => ({
        ...current,
        rainfall_1h_mm: weather.rainfall_1h_mm ?? current.rainfall_1h_mm,
        rainfall_24h_mm: weather.rainfall_24h_mm ?? current.rainfall_24h_mm,
        rainfall_72h_mm: weather.rainfall_72h_mm ?? current.rainfall_72h_mm,
        rainfall_7d_mm: weather.rainfall_7d_mm ?? current.rainfall_7d_mm,
        soil_moisture_index: weather.soil_moisture_index == null ? current.soil_moisture_index : Math.min(1, Math.max(0, weather.soil_moisture_index)),
        temperature_c: weather.temperature_c ?? current.temperature_c,
        humidity_pct: weather.humidity_pct ?? current.humidity_pct,
      }));
      setWeatherStatus(`Loaded Open-Meteo weather at ${weather.timestamp}${result.missing_fields?.length ? `; missing: ${result.missing_fields.join(", ")}` : ""}`);
    } catch (requestError) {
      setError(requestError.message);
      setWeatherStatus("Live weather unavailable; synthetic station values remain active.");
    } finally {
      setWeatherLoading(false);
    }
  }

  function exportRecentRuns() {
    const blob = new Blob([JSON.stringify(recentRuns, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `floodguard-scenarios-${new Date().toISOString().slice(0, 10)}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  function clearRecentRuns() {
    localStorage.removeItem("floodguard-scenario-runs");
    setRecentRuns([]);
  }

  function updateValue(key, value) {
    setValues((current) => ({ ...current, [key]: Number(value) }));
  }

  const Slider = ({ label, field, min, max, step, unit }) => <div className="scenario-slider"><div><span>{label}</span><strong>{values[field]} {unit}</strong></div><input type="range" min={min} max={max} step={step} value={values[field] ?? min} onChange={(event) => updateValue(field, event.target.value)} /></div>;
  const resultDelta = baseline && scenario ? scenario.predicted_risk_level - baseline.predicted_risk_level : 0;

  return <div className="content"><div className="page-intro"><p>Compare baseline versus what-if hydrological conditions. Open-Meteo weather is optional; river level and discharge remain station/synthetic unless separately integrated.</p><span className="champion-note">MIXED-PROVENANCE PREVIEW · XGBOOST</span></div><div className="scenario-layout"><div className="card scenario-controls"><CardHeader title="WHAT-IF CONTROLS" meta={station?.station_id} /><label className="scenario-station">Monitoring station<select value={stationId} onChange={(event) => setStationId(event.target.value)}>{stations.map((item) => <option key={item.station_id} value={item.station_id}>{item.station_name}</option>)}</select></label><Slider label="Rainfall · 1 hour" field="rainfall_1h_mm" min="0" max="300" step="1" unit="mm" /><Slider label="Rainfall · 24 hours" field="rainfall_24h_mm" min="0" max="500" step="1" unit="mm" /><Slider label="Rainfall · 72 hours" field="rainfall_72h_mm" min="0" max="1000" step="5" unit="mm" /><Slider label="Rainfall · 7 days" field="rainfall_7d_mm" min="0" max="1500" step="1" unit="mm" /><Slider label="River water level" field="river_water_level_m" min={Math.max(0, (station?.warning_level_m || 0) - 5)} max={(station?.danger_level_m || 300) + 5} step="0.01" unit="m" /><Slider label="Rate of rise" field="water_level_rate_of_rise_m_hr" min="-1" max="2" step="0.01" unit="m/hr" /><Slider label="Soil moisture" field="soil_moisture_index" min="0" max="1" step="0.01" unit="index" /><Slider label="Upstream discharge" field="upstream_discharge_cusecs" min="0" max="1000000" step="1000" unit="cusecs" /><Slider label="Temperature" field="temperature_c" min="-10" max="55" step="0.1" unit="°C" /><Slider label="Relative humidity" field="humidity_pct" min="0" max="100" step="1" unit="%" /><div className="weather-source-panel"><div><b>LIVE WEATHER PREVIEW</b><span>Open-Meteo · no API key</span></div><button className="outline-btn" onClick={loadLiveWeather} disabled={weatherLoading}>{weatherLoading ? "Fetching weather…" : "Load live weather"}</button>{weatherStatus && <p>{weatherStatus}</p>}</div><div className="scenario-actions"><button className="outline-btn" onClick={() => station && setValues(makeValues(station))}>Reset</button><button className="run-scenario" onClick={runComparison} disabled={loading}>{loading ? "Running model…" : "Run prediction"} <b>↗</b></button></div>{error && <div className="scenario-error">{error}</div>}</div><div className="scenario-results"><div className="card comparison-card"><CardHeader title="RISK COMPARISON" meta={scenario ? "COMPUTED" : "AWAITING INPUT"} /><div className="comparison-grid"><div><span>BASELINE</span>{baseline ? <><RiskPill label={baseline.predicted_risk_label} /><strong>{baseline.confidence * 100}% confidence</strong></> : <strong>—</strong>}</div><div className={`delta-result ${resultDelta > 0 ? "delta-up" : resultDelta < 0 ? "delta-down" : ""}`}><span>CHANGE</span><strong>{resultDelta === 0 ? "No change" : `${resultDelta > 0 ? "+" : ""}${resultDelta} tier`}</strong></div><div><span>SIMULATION</span>{scenario ? <><RiskPill label={scenario.predicted_risk_label} /><strong>{scenario.confidence * 100}% confidence</strong></> : <strong>—</strong>}</div></div></div><div className="card probability-card"><CardHeader title="CLASS PROBABILITIES" meta="SYNTHETIC DATA" />{scenario ? ["Low", "Medium", "High", "Critical"].map((label) => <div className="probability-row" key={label}><span>{label}</span><div><i style={{ width: `${(scenario.class_probabilities[label] || 0) * 100}%` }} /></div><strong>{((scenario.class_probabilities[label] || 0) * 100).toFixed(1)}%</strong></div>) : <div className="scenario-empty">Run the model to compare probability distribution.</div>}</div><div className="card drivers-card"><CardHeader title="PRIMARY RISK DRIVERS" meta="MODEL EXPLAINABILITY" /><div className="driver-list">{scenario?.primary_risk_drivers?.map((driver, index) => <div key={index}><span>{index + 1}</span><p>{driver}</p></div>) || <p className="scenario-empty">No simulation has been run.</p>}</div>  </div><div className="card recent-runs-card"><CardHeader title="RECENT SCENARIOS" meta={`${recentRuns.length} SAVED`} /><div className="recent-runs-actions"><button className="outline-btn" onClick={exportRecentRuns} disabled={!recentRuns.length}>Export JSON</button><button className="outline-btn" onClick={clearRecentRuns} disabled={!recentRuns.length}>Clear history</button></div>{recentRuns.length ? recentRuns.slice(0, 5).map((run) => <div className="recent-run" key={run.id}><div><strong>{run.station_name}</strong><span>{new Date(run.created_at).toLocaleString()}</span></div><p>{run.baseline_risk} → {run.simulated_risk}{run.tier_change ? ` · ${run.tier_change > 0 ? "+" : ""}${run.tier_change} tier` : ""}</p></div>) : <p className="scenario-empty">No locally saved scenarios.</p>}</div></div></div></div>;
}

function Incidents({ incidents, setIncidents, stations }) {
  const [stationId, setStationId] = useState(stations[0]?.station_id || "");
  const [summary, setSummary] = useState("");
  const [actor, setActor] = useState("Field Operator");
  const [error, setError] = useState("");
  const [selectedIncident, setSelectedIncident] = useState(null);
  const station = stations.find((item) => item.station_id === stationId) || stations[0];

  async function createIncident(event) {
    event.preventDefault();
    setError("");
    if (!station || !summary.trim()) {
      setError("Select a station and add a summary.");
      return;
    }
    try {
      const created = await requestJson("/api/incidents", { method: "POST", body: JSON.stringify({
        title: `${station.current_telemetry.risk_label} flood alert — ${station.station_name}`,
        station_id: station.station_id,
        station_name: station.station_name,
        river: station.river,
        risk_label: station.current_telemetry.risk_label,
        risk_level: station.current_telemetry.risk_level,
        water_level_m: station.current_telemetry.river_water_level_m,
        danger_level_m: station.danger_level_m,
        operator: actor,
        summary: summary.trim(),
      }) });
      setIncidents((current) => [created, ...current]);
      setSummary("");
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  async function openIncident(incidentId) {
    try {
      const detail = await requestJson(`/api/incidents/${incidentId}`);
      setSelectedIncident(detail);
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  async function updateIncident(incidentId, status) {
    setError("");
    const approvalRequired = status === "Acknowledged" || status === "Resolved";
    if (approvalRequired && !window.confirm(`Confirm human approval to mark this incident ${status.toLowerCase()}?`)) return;
    try {
      const updated = await requestJson(`/api/incidents/${incidentId}`, { method: "PATCH", body: JSON.stringify({ status, operator: actor, approval_confirmed: approvalRequired, note: status === "Acknowledged" ? "Acknowledged by human operator" : status === "Resolved" ? "Resolved by human operator" : "Incident moved under investigation" }) });
      setIncidents((current) => current.map((incident) => incident.id === incidentId ? updated : incident));
      if (selectedIncident?.id === incidentId) setSelectedIncident({ ...selectedIncident, ...updated });
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  return <div className="content"><div className="page-intro"><p>Human-supervised incident acknowledgement and audit workflow.</p><span className="champion-note">AI ADVICE IS NOT AN INCIDENT ACTION</span></div><div className="incident-layout"><div className="card incident-create"><CardHeader title="CREATE INCIDENT" meta="HUMAN ACTION" /><form onSubmit={createIncident}><label>Operator<input value={actor} onChange={(event) => setActor(event.target.value)} /></label><label>Station<select value={stationId} onChange={(event) => setStationId(event.target.value)}>{stations.map((item) => <option key={item.station_id} value={item.station_id}>{item.station_name}</option>)}</select></label><label>Situation summary<textarea value={summary} onChange={(event) => setSummary(event.target.value)} placeholder="Record what prompted this incident…" /></label>{error && <div className="scenario-error">{error}</div>}<button className="run-scenario" type="submit">Create incident <b>＋</b></button></form></div><div className="card incident-list"><CardHeader title="INCIDENTS" meta={`${incidents.length} TOTAL`} />{incidents.length ? incidents.map((incident) => <div className="incident-row" key={incident.id} onClick={() => openIncident(incident.id)}><div className="incident-heading"><div><strong>{incident.title}</strong><span>{incident.id} · {incident.status} · {new Date(incident.created_at).toLocaleString()}</span></div><RiskPill label={incident.risk_label} /></div><p>{incident.summary}</p><div className="incident-actions"><button onClick={(event) => { event.stopPropagation(); updateIncident(incident.id, "Investigating"); }}>Investigate</button><button onClick={(event) => { event.stopPropagation(); updateIncident(incident.id, "Acknowledged"); }}>Acknowledge</button><button onClick={(event) => { event.stopPropagation(); updateIncident(incident.id, "Resolved"); }}>Resolve</button></div></div>) : <p className="scenario-empty">No incidents have been recorded.</p>}</div><div className="card incident-detail"><CardHeader title="INCIDENT AUDIT" meta={selectedIncident?.id || "SELECT AN INCIDENT"} />{selectedIncident ? <><div className="incident-detail-status"><strong>{selectedIncident.status}</strong><RiskPill label={selectedIncident.risk_label} /></div><p className="incident-detail-summary">{selectedIncident.summary}</p><div className="audit-list">{selectedIncident.audit?.map((entry, index) => <div className="audit-entry" key={index}><b>{entry.action}</b><span>{entry.actor} · {new Date(entry.created_at).toLocaleString()}</span><p>{entry.details}</p></div>)}</div></> : <p className="scenario-empty">Select an incident to inspect its complete audit timeline.</p>}</div></div></div>;
}

function InlineMarkdown({ text }) {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) return <strong key={index}>{part.slice(2, -2)}</strong>;
    if (part.startsWith("`") && part.endsWith("`")) return <code key={index} style={{ color: "#55c9d7", background: "#091d29", padding: "1px 4px", borderRadius: 3 }}>{part.slice(1, -1)}</code>;
    return <React.Fragment key={index}>{part}</React.Fragment>;
  });
}

function AgentResponse({ text }) {
  const lines = text.split("\n");
  return <div style={{ lineHeight: 1.65, fontSize: 12, color: "#c5dadd" }}>{lines.map((line, index) => {
    const heading = line.match(/^#{2,4}\s*(.*)$/);
    if (heading) return <h4 key={index} style={{ margin: "12px 0 7px", color: "#e6f3f4", fontSize: 12, letterSpacing: ".3px" }}><InlineMarkdown text={heading[1]} /></h4>;
    if (/^---+$/.test(line.trim())) return <hr key={index} style={{ border: 0, borderTop: "1px solid #1d4051", margin: "10px 0" }} />;
    if (line.trim().startsWith("- ")) return <div key={index} style={{ display: "flex", gap: 8, margin: "5px 0" }}><span style={{ color: "#42bfd0", flex: "0 0 auto" }}>•</span><span><InlineMarkdown text={line.trim().slice(2)} /></span></div>;
    if (!line.trim()) return <div key={index} style={{ height: 7 }} />;
    return <div key={index}><InlineMarkdown text={line} /></div>;
  })}</div>;
}

function Assistant({ messages, query, setQuery, sendMessage, loadingChat }) {
  const [openTrace, setOpenTrace] = useState(null);
  return <div className="content assistant-layout"><div className="card chat-card"><CardHeader title="FLOOD INTELLIGENCE ASSISTANT" meta="REACT AGENT · HUMAN OVERSIGHT" /><div className="chat-messages">{messages.map((m, i) => <div className={`message ${m.role}`} key={i}><div className="message-avatar">{m.role === "assistant" ? "✦" : "IM"}</div><div style={{ minWidth: 0, flex: 1 }}><span className="message-role">{m.role === "assistant" ? `FLOODGUARD AI · ${m.synthesisSource === "gemini" ? "GEMINI ENHANCED" : "OFFLINE FALLBACK"}` : "YOU"}</span>{m.role === "assistant" ? <AgentResponse text={m.text} /> : <p>{m.text}</p>}{m.trace?.length > 0 && <div><button className="trace-btn" onClick={() => setOpenTrace(openTrace === i ? null : i)}>{openTrace === i ? "▾" : "▸"} View tool trace ({m.trace.length})</button>{openTrace === i && <div style={{ marginTop: 10, border: "1px solid #254f60", borderRadius: 5, padding: 10, background: "#091e2b" }}>{m.plan?.length > 0 && <div style={{ marginBottom: 9 }}><strong style={{ color: "#55c9d7", fontSize: 9, letterSpacing: 1 }}>INVESTIGATION PLAN</strong>{m.plan.map((step, stepIndex) => <div key={stepIndex} style={{ color: "#91abb4", fontSize: 10, marginTop: 5 }}>{stepIndex + 1}. {step}</div>)}</div>}<strong style={{ color: "#55c9d7", fontSize: 9, letterSpacing: 1 }}>MCP TOOL CALLS</strong>{m.trace.map((call, callIndex) => <div key={callIndex} style={{ borderTop: "1px solid #1c3b4b", marginTop: 7, paddingTop: 7 }}><b style={{ color: "#bfe0e5", fontSize: 10 }}>{call.tool}</b><div style={{ color: "#91abb4", fontSize: 10, marginTop: 3 }}>{call.summary}</div></div>)}</div>}</div>}</div></div>)}{loadingChat && <div className="message assistant"><div className="message-avatar">✦</div><p className="typing">Analyzing telemetry <i /> <i /> <i /></p></div>}</div><form className="chat-input" onSubmit={sendMessage}><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Ask about flood risk, stations, or preparedness…" /><button>Send <b>↗</b></button></form></div><div className="card prompt-card"><h3>TRY ASKING</h3>{["What can you do?", "Which stations need immediate attention?", "Summarize Yamuna risk factors", "What is the recommended response for High risk?"].map((q) => <button key={q} onClick={() => setQuery(q)}>{q}<span>→</span></button>)}<div className="safety-note"><b>◎ Human-in-the-loop</b><p>AI outputs are advisory. Verify all recommendations against official CWC and NDMA bulletins before action.</p></div></div></div>;
}

createRoot(document.getElementById("root")).render(<App />);
