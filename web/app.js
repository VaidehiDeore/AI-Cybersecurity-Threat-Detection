const $ = (id) => document.getElementById(id);
const state = { traffic: [], alerts: [] };
const pageMeta = {
  overview: ["AI-POWERED CYBERSECURITY / OVERVIEW", "Threat intelligence <span>dashboard</span>"],
  monitor: ["NETWORK TELEMETRY / LIVE MONITOR", "Live traffic <span>monitor</span>"],
  alerts: ["TRIAGE & INVESTIGATION / ALERT CENTER", "Threat <span>alert center</span>"],
  analytics: ["MODEL OBSERVABILITY / ANALYTICS", "Detection <span>analytics</span>"]
};
const fmtPct = (v) => v == null || Number.isNaN(Number(v)) ? "—" : `${(Number(v) * 100).toFixed(1)}%`;
const fmtNum = (v) => v == null ? "—" : Number(v).toLocaleString(undefined, {maximumFractionDigits: 2});
async function getJSON(url) {
  const response = await fetch(url);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Request failed: ${response.status}`);
  return data;
}
function toast(message) {
  const el = $("toast"); el.textContent = message; el.classList.add("show");
  window.setTimeout(() => el.classList.remove("show"), 2800);
}
function goToPage(name) {
  if (!pageMeta[name]) return;
  document.querySelectorAll(".page").forEach(el => el.classList.toggle("active", el.id === `page-${name}`));
  document.querySelectorAll(".nav-item").forEach(el => el.classList.toggle("active", el.dataset.page === name));
  $("page-eyebrow").textContent = pageMeta[name][0];
  $("page-title").innerHTML = pageMeta[name][1];
  if (name === "monitor") loadTraffic().catch(e => toast(e.message));
  if (name === "analytics") loadAnalytics().catch(e => toast(e.message));
  if (name === "alerts" && state.alerts.length === 0) runDetection();
  window.scrollTo({top: 0, behavior: "smooth"});
}
document.querySelectorAll(".nav-item").forEach(el => el.addEventListener("click", () => goToPage(el.dataset.page)));
document.querySelectorAll("[data-goto]").forEach(el => el.addEventListener("click", () => goToPage(el.dataset.goto)));
function renderDistribution(counts, target = "distribution") {
  const container = $(target);
  const entries = Object.entries(counts || {}).sort((a,b) => b[1]-a[1]);
  if (!entries.length) { container.innerHTML = '<div class="empty">No class data available.</div>'; return; }
  const max = Math.max(...entries.map(e => Number(e[1])), 1);
  container.innerHTML = entries.map(([label, count]) => {
    const threat = label !== "NORMAL";
    return `<div class="bar-row"><span>${label.replaceAll("_"," ")}</span><div class="bar-track"><div class="bar-fill ${threat ? "threat-fill" : ""}" style="width:${(count/max)*100}%"></div></div><b>${Number(count).toLocaleString()}</b></div>`;
  }).join("");
}
async function loadSummary() {
  const [summary, health] = await Promise.all([getJSON("/api/summary"), getJSON("/api/health")]);
  $("total-flows").textContent = fmtNum(summary.total_flows);
  const m = summary.metrics || {};
  $("accuracy").textContent = fmtPct(m.accuracy);
  $("precision").textContent = fmtPct(m.precision);
  $("recall").textContent = fmtPct(m.recall);
  $("f1").textContent = fmtPct(m.f1);
  $("score-ring").style.setProperty("--score-deg", `${(m.f1 || 0) * 360}deg`);
  $("score-ring").style.background = `conic-gradient(var(--cyan) ${(m.f1 || 0)*360}deg, #e6eff7 0deg)`;
  $("engine-status").textContent = health.model_ready ? "Model loaded · ready" : "Train model to activate";
  renderDistribution(summary.label_counts);
}
function severityClass(severity) { return `severity sev-${String(severity || "MEDIUM").toUpperCase()}`; }
function renderAlerts(alerts) {
  state.alerts = alerts || [];
  const rows = state.alerts.map(a => {
    const label = a.predicted_label || "UNKNOWN", severity = a.severity || "MEDIUM";
    const time = new Date(a.timestamp).toLocaleTimeString();
    return `<tr><td><span class="${severityClass(severity)}">${severity}</span></td><td><b>${label.replaceAll("_"," ")}</b></td><td class="confidence">${fmtPct(a.confidence)}</td><td class="${a.threat_detected ? "threat-yes" : "threat-no"}">${a.threat_detected ? "⚠ THREAT FLAGGED" : "✓ NORMAL"}</td><td>${time}</td></tr>`;
  }).join("");
  if ($("alert-rows")) $("alert-rows").innerHTML = rows || '<tr><td colspan="5" class="empty">No predictions returned.</td></tr>';
  const threats = state.alerts.filter(a => a.threat_detected).length;
  if ($("alert-total")) $("alert-total").textContent = state.alerts.length;
  if ($("alert-threats")) $("alert-threats").textContent = threats;
  const rank = {INFO: 0, MEDIUM: 1, HIGH: 2, CRITICAL: 3};
  const highest = state.alerts.reduce((best, a) => (rank[a.severity] || 0) > (rank[best] || 0) ? a.severity : best, "INFO");
  if ($("alert-highest")) $("alert-highest").textContent = state.alerts.length ? highest : "—";
  if ($("overview-alert-list")) {
    $("overview-alert-list").innerHTML = state.alerts.slice(0, 3).map(a =>
      `<div class="mini-alert"><span class="${severityClass(a.severity)}">${a.severity}</span><div><b>${(a.predicted_label || "UNKNOWN").replaceAll("_"," ")}</b><small>${a.threat_detected ? "Threat pattern flagged" : "No threat predicted"}</small></div><span class="mini-confidence">${fmtPct(a.confidence)}</span></div>`
    ).join("") || '<div class="empty">No detections yet.</div>';
  }
}
async function runDetection() {
  const button = $("run-detection");
  if (button) { button.disabled = true; button.textContent = "Running…"; }
  try {
    const data = await getJSON("/api/alerts");
    renderAlerts(data.alerts);
    toast(`Detection complete · ${data.alerts.filter(a => a.threat_detected).length} suspicious predictions`);
  } catch (e) { toast(e.message); }
  finally { if (button) { button.disabled = false; button.textContent = "▶ Run demo detection"; } }
}
function renderTraffic(records) {
  state.traffic = records || [];
  const selected = $("traffic-filter") ? $("traffic-filter").value : "ALL";
  const rows = state.traffic.filter(r => selected === "ALL" || r.label === selected).map(r => {
    const severity = ({NORMAL:"INFO", ANOMALY:"MEDIUM", BRUTE_FORCE:"HIGH", DOS:"CRITICAL"})[r.label] || "MEDIUM";
    return `<tr><td><span class="${severityClass(severity)}">${String(r.label).replaceAll("_"," ")}</span></td><td>${r.service}</td><td>${fmtNum(r.request_rate)}</td><td>${fmtNum(r.connection_count)}</td><td>${fmtNum(r.failed_logins)}</td><td>${fmtNum(r.src_bytes)} / ${fmtNum(r.dst_bytes)}</td></tr>`;
  }).join("");
  $("traffic-rows").innerHTML = rows || '<tr><td colspan="6" class="empty">No rows match this filter.</td></tr>';
}
async function loadTraffic() {
  const data = await getJSON("/api/traffic");
  const analytics = await getJSON("/api/analytics");
  $("monitor-count").textContent = data.records.length;
  $("monitor-high").textContent = fmtNum(analytics.feature_summary.high_request_rate_flows);
  $("monitor-avg").textContent = fmtNum(analytics.feature_summary.avg_connections);
  renderTraffic(data.records);
}
async function loadAnalytics() {
  const data = await getJSON("/api/analytics");
  const m = data.metrics || {}, f = data.feature_summary || {};
  $("ana-precision").textContent = fmtPct(m.precision_weighted);
  $("ana-recall").textContent = fmtPct(m.recall_weighted);
  $("ana-f1").textContent = fmtPct(m.f1_weighted);
  $("avg-rate").textContent = fmtNum(f.avg_request_rate);
  $("avg-connections").textContent = fmtNum(f.avg_connections);
  $("avg-failed").textContent = fmtNum(f.avg_failed_logins);
  $("high-rate").textContent = fmtNum(f.high_request_rate_flows);
  renderDistribution(data.label_counts, "analytics-distribution");
}
$("refresh-btn").addEventListener("click", async () => {
  try { await loadSummary(); const active = document.querySelector(".nav-item.active")?.dataset.page; if (active === "monitor") await loadTraffic(); if (active === "analytics") await loadAnalytics(); toast("Dashboard data refreshed"); }
  catch (e) { toast(e.message); }
});
$("monitor-refresh").addEventListener("click", () => loadTraffic().then(() => toast("Traffic records refreshed")).catch(e => toast(e.message)));
$("analytics-refresh").addEventListener("click", () => loadAnalytics().then(() => toast("Analytics refreshed")).catch(e => toast(e.message)));
$("run-detection").addEventListener("click", runDetection);
$("traffic-filter").addEventListener("change", () => renderTraffic(state.traffic));
loadSummary().then(() => runDetection()).catch(e => { $("engine-status").textContent = "API unavailable"; toast(e.message); });
