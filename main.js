/**
 * SNP · Research consolidated JavaScript Controller.
 * Manages parent view navigation (home, goldstein, chc, caligula),
 * coordinates dynamic serverless API calls for Caligula, and
 * builds premium, high-performance HTML/SVG vector charts.
 */

(function() {
    // ── Configuration ──────────────────────────────────────────────────────────
    // Uses Vercel's relative endpoints in production, fallbacks to localhost in dev
    let API_BASE = window.location.origin;
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        if (window.location.port && window.location.port !== '3000') {
            API_BASE = `${window.location.protocol}//${window.location.hostname}:3000`;
        }
    } else if (window.location.protocol === 'file:' || !window.location.hostname) {
        API_BASE = 'http://127.0.0.1:3000';
    }

    const PILLAR_KEYS = [
        "unit_economics_score",
        "capital_discipline_score",
        "balance_sheet_score",
        "hedge_book_score",
        "reserves_score",
        "operational_score",
        "sentiment_score",
        "macro_sensitivity_score"
    ];

    const PILLAR_LABELS = [
        "Unit Economics",
        "Capital Discipline",
        "Balance Sheet",
        "Hedge Book / Liq.",
        "Reserves & Inv.",
        "Operational",
        "Sentiment",
        "Macro Sensitivity"
    ];

    // ── State management & parent view toggling ──────────────────────────────────
    const VIEWS = ['home', 'goldstein', 'chc', 'caligula'];
    let activeView = 'home';

    function setView(name, push) {
        if (!VIEWS.includes(name)) name = 'home';
        activeView = name;

        // Toggle active page views
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        const el = document.getElementById('view-' + name);
        if (el) el.classList.add('active');

        // Toggle active navbar buttons
        document.querySelectorAll('[data-view]').forEach(b => {
            b.classList.toggle('is-active', b.getAttribute('data-view') === name);
        });

        // Dynamic Document Titles
        document.title = name === 'home'
            ? 'SNP · Research'
            : name === 'goldstein'
                ? 'Project Goldstein — SNP · Research'
                : name === 'chc'
                    ? 'CHC Platform — SNP · Research'
                    : 'Project Caligula — SNP · Research';

        if (push) {
            try {
                history.pushState({ v: name }, '', '#' + name);
            } catch (e) {
                try {
                    window.location.hash = name;
                } catch (hashErr) {
                    console.warn("History pushState and hash fallback failed:", hashErr);
                }
            }
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });

        // Auto-load Caligula rankings if navigating to Caligula for the first time
        if (name === 'caligula') {
            setCaligulaSubview('rankings');
            loadUniverseRankings();
        }
    }

    function fromHash() {
        const h = (location.hash || '').replace('#', '').toLowerCase();
        setView(VIEWS.includes(h) ? h : 'home', false);
    }

    // ── Caligula Sub-view Toggling ──────────────────────────────────────────────
    let activeCaligulaSubview = 'rankings';
    const subbtnRanks = document.getElementById('subbtn-rankings');
    const subbtnBacktest = document.getElementById('subbtn-backtest');
    
    const subviewRanks = document.getElementById('caligula-rankings-subview');
    const subviewBacktest = document.getElementById('caligula-backtest-subview');
    const subviewDeepdive = document.getElementById('caligula-deepdive-subview');

    function setCaligulaSubview(subviewName) {
        activeCaligulaSubview = subviewName;
        if (subviewRanks) subviewRanks.classList.remove('active');
        if (subviewBacktest) subviewBacktest.classList.remove('active');
        if (subviewDeepdive) subviewDeepdive.classList.remove('active');

        if (subviewName === 'rankings') {
            if (subviewRanks) subviewRanks.classList.add('active');
            if (subbtnRanks) {
                subbtnRanks.style.background = "var(--ink)";
                subbtnRanks.style.color = "var(--p)";
            }
            if (subbtnBacktest) {
                subbtnBacktest.style.background = "transparent";
                subbtnBacktest.style.color = "var(--ink)";
            }
        } else if (subviewName === 'backtest') {
            if (subviewBacktest) subviewBacktest.classList.add('active');
            if (subbtnBacktest) {
                subbtnBacktest.style.background = "var(--ink)";
                subbtnBacktest.style.color = "var(--p)";
            }
            if (subbtnRanks) {
                subbtnRanks.style.background = "transparent";
                subbtnRanks.style.color = "var(--ink)";
            }
            loadBacktestData('ep_study'); // Default backtest toggle
        } else if (subviewName === 'deepdive') {
            if (subviewDeepdive) subviewDeepdive.classList.add('active');
        }
    }

    // ── Caligula Rankings Ingestion ──────────────────────────────────────────────
    async function loadUniverseRankings() {
        const tbody = document.getElementById('universe-tbody');
        if (!tbody) return;
        try {
            const res = await fetch(`${API_BASE}/api/universe`);
            if (!res.ok) throw new Error("API universe fetch failed");
            
            let data;
            try {
                data = await res.json();
            } catch (jsonErr) {
                throw new Error("Invalid response format received from server");
            }

            if (!data.rankings || data.rankings.length === 0) {
                tbody.innerHTML = `<tr><td colspan="12" class="td-sub" style="text-align: center; padding: 40px 0;">No active study rankings compiled.</td></tr>`;
                return;
            }

            let rowsHtml = '';
            data.rankings.forEach(row => {
                const tierClass = row.tier === 'A' ? 'td-good' : row.tier === 'B' ? 'td-warn' : row.tier === 'C' ? 'td-risk' : '';
                
                rowsHtml += `
                    <tr style="cursor: pointer;" data-ticker="${row.ticker}">
                        <td class="td-sub">${row.rank}</td>
                        <td style="font-weight: 600; color: var(--ink);">${row.ticker}</td>
                        <td class="${tierClass}">${row.tier}</td>
                        <td style="font-family: var(--mono); font-weight: bold; color: var(--go);">${row.caligula_score.toFixed(3)}</td>
                        <td style="font-family: var(--mono);">${row.unit_economics_score.toFixed(2)}</td>
                        <td style="font-family: var(--mono);">${row.capital_discipline_score.toFixed(2)}</td>
                        <td style="font-family: var(--mono);">${row.balance_sheet_score.toFixed(2)}</td>
                        <td style="font-family: var(--mono);">${row.hedge_book_score.toFixed(2)}</td>
                        <td style="font-family: var(--mono);">${row.reserves_score.toFixed(2)}</td>
                        <td style="font-family: var(--mono);">${row.operational_score.toFixed(2)}</td>
                        <td style="font-family: var(--mono);">${row.sentiment_score.toFixed(2)}</td>
                        <td style="font-family: var(--mono);">${row.macro_sensitivity_score.toFixed(2)}</td>
                    </tr>
                `;
            });
            tbody.innerHTML = rowsHtml;

            // Bind click-to-deep-dive triggers to rankings rows!
            tbody.querySelectorAll('tr').forEach(tr => {
                tr.addEventListener('click', () => {
                    const symbol = tr.dataset.ticker;
                    if (symbol) runDiligenceAnalysis(symbol);
                });
            });

        } catch (err) {
            console.error(err);
            tbody.innerHTML = `<tr><td colspan="12" class="td-sub" style="text-align: center; padding: 40px 0; color: var(--go);">Unable to fetch study rankings. Dev fallback active.</td></tr>`;
        }
    }

    // ── Dynamic SVG Radar Chart Builder ──────────────────────────────────────────
    function drawRadarChart(scores) {
        const cx = 250;
        const cy = 180;
        const maxRadius = 110;
        const numPillars = 8;
        
        let svg = `
        <svg viewBox="0 0 500 360" width="100%" height="100%">
            <!-- Concentric Grid Circles -->
        `;
        
        for (let j = 1; j <= 5; j++) {
            const r = (j / 5) * maxRadius;
            svg += `<circle cx="${cx}" cy="${cy}" r="${r}" stroke="rgba(17,16,8,0.06)" fill="none" stroke-width="1" />`;
            if (j === 3 || j === 5) {
                svg += `<text x="${cx + 4}" y="${cy - r + 3}" fill="var(--gh)" font-family="var(--mono)" font-size="7" opacity="0.6">${(j/5).toFixed(1)}</text>`;
            }
        }

        const polygonPoints = [];
        for (let i = 0; i < numPillars; i++) {
            const angle = (i * 2 * Math.PI / numPillars) - (Math.PI / 2);
            
            const ax = cx + maxRadius * Math.cos(angle);
            const ay = cy + maxRadius * Math.sin(angle);
            svg += `<line x1="${cx}" y1="${cy}" x2="${ax}" y2="${ay}" stroke="rgba(17,16,8,0.06)" stroke-width="1" />`;
            
            const scoreVal = scores[i] || 0.5;
            const vx = cx + maxRadius * scoreVal * Math.cos(angle);
            const vy = cy + maxRadius * scoreVal * Math.sin(angle);
            polygonPoints.push(`${vx},${vy}`);

            let offsetMultiplier = 1.25;
            let lx = cx + maxRadius * offsetMultiplier * Math.cos(angle);
            let ly = cy + maxRadius * offsetMultiplier * Math.sin(angle);
            
            let anchor = "middle";
            if (Math.cos(angle) > 0.1) anchor = "start";
            if (Math.cos(angle) < -0.1) anchor = "end";
            if (Math.abs(Math.sin(angle)) > 0.9) ly += (Math.sin(angle) > 0 ? 4 : -2);

            svg += `
            <text x="${lx}" y="${ly}" fill="var(--ink)" font-family="var(--serif)" font-size="11" font-weight="500" text-anchor="${anchor}">
                ${PILLAR_LABELS[i]}
                <tspan x="${lx}" dy="10" font-family="var(--mono)" font-size="8" fill="var(--go)">${scoreVal.toFixed(2)}</tspan>
            </text>
            `;
        }

        const pointsString = polygonPoints.join(' ');
        svg += `
            <polygon points="${pointsString}" fill="rgba(184, 146, 42, 0.16)" stroke="var(--go)" stroke-width="2" />
        `;

        polygonPoints.forEach(pt => {
            const [x, y] = pt.split(',');
            svg += `<circle cx="${x}" cy="${y}" r="3" fill="var(--ink)" stroke="var(--go)" stroke-width="1" />`;
        });

        svg += `</svg>`;
        return svg;
    }

    // ── Dynamic SVG History Line Chart Builder (Option B) ─────────────────────────
    function drawHistoryLineChart(history) {
        if (!history || history.length === 0) return `<div class="td-sub">No historical quality path available.</div>`;
        
        const w = 600;
        const h = 260;
        const padL = 50;
        const padR = 20;
        const padT = 20;
        const padB = 40;
        
        const chartW = w - padL - padR;
        const chartH = h - padT - padB;
        
        const quarters = history.map(d => d.quarter);
        const scores = history.map(d => d.caligula_score || 0.5);
        
        const minVal = 0.0;
        const maxVal = 1.0;
        
        let points = [];
        for (let i = 0; i < history.length; i++) {
            const x = padL + (i / (history.length - 1 || 1)) * chartW;
            const y = padT + chartH - ((scores[i] - minVal) / (maxVal - minVal)) * chartH;
            points.push({ x, y, score: scores[i], label: quarters[i] });
        }
        
        let svg = `
        <svg viewBox="0 0 ${w} ${h}" width="100%" height="100%">
            <!-- Y-Axis Grid Lines & Ticks -->
        `;
        for (let j = 0; j <= 4; j++) {
            const yVal = minVal + (j / 4) * (maxVal - minVal);
            const yPos = padT + chartH - (j / 4) * chartH;
            svg += `
                <line x1="${padL}" y1="${yPos}" x2="${w - padR}" y2="${yPos}" stroke="rgba(17,16,8,0.06)" stroke-width="1" />
                <text x="${padL - 10}" y="${yPos + 3}" fill="var(--gh)" font-family="var(--mono)" font-size="7.5" text-anchor="end">${yVal.toFixed(2)}</text>
            `;
        }
        
        // X-Axis Quarters
        const step = Math.max(1, Math.floor(history.length / 5));
        points.forEach((pt, idx) => {
            if (idx % step === 0 || idx === history.length - 1) {
                svg += `
                    <line x1="${pt.x}" y1="${padT}" x2="${pt.x}" y2="${padT + chartH}" stroke="rgba(17,16,8,0.03)" stroke-dasharray="2,2" stroke-width="1" />
                    <text x="${pt.x}" y="${padT + chartH + 18}" fill="var(--gh)" font-family="var(--mono)" font-size="7.5" text-anchor="middle">
                        ${pt.label.length > 7 ? pt.label.substring(2,7) : pt.label}
                    </text>
                `;
            }
        });
        
        // Draw Area Shading
        let pathString = `M ${points[0].x} ${padT + chartH}`;
        points.forEach(pt => { pathString += ` L ${pt.x} ${pt.y}`; });
        pathString += ` L ${points[points.length - 1].x} ${padT + chartH} Z`;
        svg += `<path d="${pathString}" fill="rgba(184,146,42,0.08)" stroke="none" />`;
        
        // Draw Core Line
        let lineString = `M ${points[0].x} ${points[0].y}`;
        for (let i = 1; i < points.length; i++) {
            lineString += ` L ${points[i].x} ${points[i].y}`;
        }
        svg += `<path d="${lineString}" fill="none" stroke="var(--go)" stroke-width="2" />`;
        
        // Draw Dots
        points.forEach(pt => {
            svg += `
                <circle cx="${pt.x}" cy="${pt.y}" r="3" fill="var(--ink)" stroke="var(--go)" stroke-width="1" />
            `;
        });
        
        svg += `</svg>`;
        return svg;
    }

    // ── Dynamic SVG Backtest Line Chart Builder (Option B & C) ────────────────────
    function drawBacktestLineChart(series) {
        if (!series || series.length === 0) return `<div class="td-sub">No backtest data loaded.</div>`;
        
        const w = 600;
        const h = 320;
        const padL = 50;
        const padR = 20;
        const padT = 30;
        const padB = 40;
        
        const chartW = w - padL - padR;
        const chartH = h - padT - padB;
        
        const cumLS = series.map(d => d.cum_ls);
        const cumLong = series.map(d => d.cum_long);
        const cumShort = series.map(d => d.cum_short);
        
        const allVals = cumLS.concat(cumLong).concat(cumShort);
        const minVal = Math.max(0.0, Math.min(...allVals) * 0.9);
        const maxVal = Math.max(...allVals) * 1.1;
        
        let ptsLS = [], ptsLong = [], ptsShort = [];
        series.forEach((d, idx) => {
            const x = padL + (idx / (series.length - 1 || 1)) * chartW;
            ptsLS.push({ x, y: padT + chartH - ((d.cum_ls - minVal) / (maxVal - minVal)) * chartH });
            ptsLong.push({ x, y: padT + chartH - ((d.cum_long - minVal) / (maxVal - minVal)) * chartH });
            ptsShort.push({ x, y: padT + chartH - ((d.cum_short - minVal) / (maxVal - minVal)) * chartH });
        });
        
        let svg = `
        <svg viewBox="0 0 ${w} ${h}" width="100%" height="100%">
            <!-- Legend -->
            <g transform="translate(${padL}, 12)">
                <line x1="0" y1="5" x2="20" y2="5" stroke="var(--go)" stroke-width="2.5" />
                <text x="25" y="9" fill="var(--ink)" font-family="var(--serif)" font-size="9" font-weight="600">Long-Short L/S</text>
                
                <line x1="110" y1="5" x2="130" y2="5" stroke="var(--ink)" stroke-dasharray="2,2" stroke-width="1.5" />
                <text x="135" y="9" fill="var(--ink)" font-family="var(--serif)" font-size="9" font-weight="600">Long Only</text>
                
                <line x1="210" y1="5" x2="230" y2="5" stroke="var(--ash)" stroke-dasharray="2,2" stroke-width="1.5" />
                <text x="235" y="9" fill="var(--ink)" font-family="var(--serif)" font-size="9" font-weight="600">Short Only</text>
            </g>
        `;
        
        for (let j = 0; j <= 5; j++) {
            const yVal = minVal + (j / 5) * (maxVal - minVal);
            const yPos = padT + chartH - (j / 5) * chartH;
            svg += `
                <line x1="${padL}" y1="${yPos}" x2="${w - padR}" y2="${yPos}" stroke="rgba(17,16,8,0.06)" stroke-width="1" />
                <text x="${padL - 10}" y="${yPos + 3}" fill="var(--gh)" font-family="var(--mono)" font-size="7.5" text-anchor="end">${yVal.toFixed(2)}</text>
            `;
        }
        
        const step = Math.max(1, Math.floor(series.length / 6));
        series.forEach((d, idx) => {
            if (idx % step === 0 || idx === series.length - 1) {
                const x = padL + (idx / (series.length - 1 || 1)) * chartW;
                svg += `
                    <line x1="${x}" y1="${padT}" x2="${x}" y2="${padT + chartH}" stroke="rgba(17,16,8,0.03)" stroke-dasharray="2,2" stroke-width="1" />
                    <text x="${x}" y="${padT + chartH + 18}" fill="var(--gh)" font-family="var(--mono)" font-size="7.5" text-anchor="middle">
                        ${d.quarter.substring(2,7)}
                    </text>
                `;
            }
        });
        
        autoDrawPath(ptsShort, 'var(--ash)', '1.5', '3,3');
        autoDrawPath(ptsLong, 'var(--ink)', '1.5', '2,2');
        autoDrawPath(ptsLS, 'var(--go)', '2.5', 'none');
        
        function autoDrawPath(pts, color, width, dash) {
            let str = `M ${pts[0].x} ${pts[0].y}`;
            for (let i = 1; i < pts.length; i++) { str += ` L ${pts[i].x} ${pts[i].y}`; }
            svg += `<path d="${str}" fill="none" stroke="${color}" stroke-width="${width}" stroke-dasharray="${dash}" />`;
        }
        
        svg += `</svg>`;
        return svg;
    }

    // ── Dynamic SVG Backtest Bar Chart Builder (Option B & C) ─────────────────────
    function drawBacktestBarChart(series) {
        if (!series || series.length === 0) return `<div class="td-sub">No backtest data loaded.</div>`;
        
        const w = 600;
        const h = 320;
        const padL = 50;
        const padR = 20;
        const padT = 30;
        const padB = 40;
        
        const chartW = w - padL - padR;
        const chartH = h - padT - padB;
        
        const rets = series.map(d => d.ls_return);
        const minVal = Math.min(-0.15, Math.min(...rets) * 1.2);
        const maxVal = Math.max(0.15, Math.max(...rets) * 1.2);
        
        let svg = `
        <svg viewBox="0 0 ${w} ${h}" width="100%" height="100%">
            <text x="${padL}" y="15" fill="var(--ink)" font-family="var(--serif)" font-size="9" font-weight="600" text-anchor="start">
                Quarterly L/S Returns (%)
            </text>
        `;
        
        for (let j = 0; j <= 4; j++) {
            const yVal = minVal + (j / 4) * (maxVal - minVal);
            const yPos = padT + chartH - (j / 4) * chartH;
            svg += `
                <line x1="${padL}" y1="${yPos}" x2="${w - padR}" y2="${yPos}" stroke="rgba(17,16,8,0.06)" stroke-width="1" />
                <text x="${padL - 10}" y="${yPos + 3}" fill="var(--gh)" font-family="var(--mono)" font-size="7.5" text-anchor="end">${(yVal * 100).toFixed(0)}%</text>
            `;
        }
        
        const yZero = padT + chartH - ((0.0 - minVal) / (maxVal - minVal)) * chartH;
        svg += `<line x1="${padL}" y1="${yZero}" x2="${w - padR}" y2="${yZero}" stroke="var(--ink)" stroke-width="1.5" />`;
        
        const barW = Math.max(2, (chartW / series.length) * 0.6);
        series.forEach((d, idx) => {
            const x = padL + (idx / (series.length - 1 || 1)) * chartW;
            const yVal = d.ls_return;
            const yPos = padT + chartH - ((yVal - minVal) / (maxVal - minVal)) * chartH;
            
            const barH = Math.abs(yPos - yZero);
            const barY = yVal >= 0 ? yPos : yZero;
            const color = yVal >= 0 ? "var(--go)" : "var(--ink)";
            
            svg += `
                <rect x="${x - barW/2}" y="${barY}" width="${barW}" height="${barH}" fill="${color}" opacity="0.85" />
            `;
        });
        
        const step = Math.max(1, Math.floor(series.length / 6));
        series.forEach((d, idx) => {
            if (idx % step === 0 || idx === series.length - 1) {
                const x = padL + (idx / (series.length - 1 || 1)) * chartW;
                svg += `
                    <text x="${x}" y="${padT + chartH + 18}" fill="var(--gh)" font-family="var(--mono)" font-size="7.5" text-anchor="middle">
                        ${d.quarter.substring(2,7)}
                    </text>
                `;
            }
        });
        
        svg += `</svg>`;
        return svg;
    }

    // ── Query Diligence Analysis Route ──────────────────────────────────────────
    async function runDiligenceAnalysis(ticker) {
        const symbol = ticker.toUpperCase().trim();
        if (!symbol) return;

        const loader = document.getElementById('api-loader');
        const errorMsg = document.getElementById('search-error-msg');
        
        if (errorMsg) errorMsg.textContent = '';
        if (loader) loader.style.display = 'block';
        
        try {
            const res = await fetch(`${API_BASE}/api/analyze?ticker=${symbol}`);
            if (!res.ok) {
                let errMsg = "Analysis query failed";
                try {
                    const errData = await res.json();
                    errMsg = errData.detail || errMsg;
                } catch (jsonErr) {
                    try {
                        const errText = await res.text();
                        if (errText && errText.length < 150) {
                            errMsg = errText;
                        } else {
                            errMsg = `Server returned status ${res.status}`;
                        }
                    } catch (textErr) {
                        errMsg = `Server returned status ${res.status}`;
                    }
                }
                throw new Error(errMsg);
            }
            const data = await res.json();
            if (loader) loader.style.display = 'none';

            // Navigate to Caligula deep-dive subview
            setCaligulaSubview('deepdive');

            const latest = data.latest;

            // Fill header details
            document.getElementById('dd-kicker').innerHTML = `${data.type === 'ep_study' ? 'E&P Study Operator' : 'Corporate Equities'} &nbsp;·&nbsp; ${symbol}`;
            document.getElementById('dd-title').innerHTML = `${latest.name || symbol} <em>Analysis</em>`;
            document.getElementById('dd-meta').innerHTML = `${latest.sector} &nbsp;·&nbsp; ${latest.industry} &nbsp;·&nbsp; ${latest.quarter}`;

            // Build Stat Strip
            const strip = document.getElementById('dd-stat-strip');
            strip.innerHTML = `
                <div class="stat-cell">
                    <div class="stat-num">${latest.caligula_score.toFixed(3)}</div>
                    <div class="stat-key">Composite Score</div>
                </div>
                <div class="stat-cell">
                    <div class="stat-num"><em>Tier ${latest.tier}</em></div>
                    <div class="stat-key">Diligence Rating</div>
                </div>
                <div class="stat-cell">
                    <div class="stat-num">${latest.quarter}</div>
                    <div class="stat-key">Reporting Period</div>
                </div>
                <div class="stat-cell">
                    <div class="stat-num" style="font-size: 14px; padding-top: 10px; font-family: var(--mono); text-transform: uppercase; line-height:1.2;">
                        ${latest.industry.split(' ').slice(0, 2).join(' ')}
                    </div>
                    <div class="stat-key">Sector Class</div>
                </div>
            `;

            // Draw SVG Radar
            const scoresArray = PILLAR_KEYS.map(k => latest[k] || 0.5);
            document.getElementById('dd-chart-container').innerHTML = drawRadarChart(scoresArray);

            // Draw SVG History Line Chart (Option B visual upgrade)
            if (data.history && data.history.length > 0) {
                document.getElementById('dd-history-chart-container').innerHTML = drawHistoryLineChart(data.history);
            } else {
                document.getElementById('dd-history-chart-container').innerHTML = `<div class="td-sub" style="text-align:center; padding:40px;">Quality evolutionary trends will populate here.</div>`;
            }

            // Populate Metrics Ledger
            const tbody = document.getElementById('dd-metrics-tbody');
            let metricsHtml = '';

            PILLAR_KEYS.forEach((key, idx) => {
                const score = latest[key] || 0.5;
                const scoreClass = score >= 0.70 ? 'td-good' : score >= 0.50 ? 'td-warn' : 'td-risk';
                
                let valDesc = 'Ingested footnote resolved';
                if (latest.raw_metrics) {
                    const raw = latest.raw_metrics;
                    if (key.includes('unit_economics')) {
                        valDesc = raw.gross_margin ? `Gross Margin: ${(raw.gross_margin*100).toFixed(0)}%` : 'Baseline geological costs';
                    } else if (key.includes('capital_discipline')) {
                        valDesc = raw.roa ? `ROA: ${(raw.roa*100).toFixed(1)}%` : 'FCF payout coverage';
                    } else if (key.includes('balance_sheet')) {
                        valDesc = raw.debt_ebitda ? `Debt/EBITDA: ${raw.debt_ebitda.toFixed(1)}x` : 'Net Leverage Buffer';
                    } else if (key.includes('hedge_book')) {
                        valDesc = raw.quick_ratio ? `Quick Ratio: ${raw.quick_ratio.toFixed(2)}x` : 'Hedge floors parsed';
                    } else if (key.includes('reserves')) {
                        valDesc = raw.revenue_growth ? `Revenue Growth: ${(raw.revenue_growth*100).toFixed(0)}%` : 'Inventory replacements';
                    } else if (key.includes('operational')) {
                        valDesc = raw.roe ? `ROE: ${(raw.roe*100).toFixed(0)}%` : 'Engineering gains';
                    } else if (key.includes('sentiment')) {
                        valDesc = raw.short_pct ? `Short Float: ${(raw.short_pct*100).toFixed(1)}%` : 'Short sale indicators';
                    } else if (key.includes('macro')) {
                        valDesc = raw.beta ? `Beta Coefficient: ${raw.beta.toFixed(2)}` : 'Market crash protection';
                    }
                }

                metricsHtml += `
                    <tr>
                        <td style="font-weight: 500;">${PILLAR_LABELS[idx]}</td>
                        <td class="td-sub">${valDesc}</td>
                        <td class="${scoreClass}" style="font-family: var(--mono);">${score.toFixed(2)}</td>
                    </tr>
                `;
            });
            tbody.innerHTML = metricsHtml;

        } catch (err) {
            console.error(err);
            if (loader) loader.style.display = 'none';
            if (errorMsg) errorMsg.textContent = err.message || "Unable to parse and score stock.";
        }
    }

    // ── Ingest and Populate Backtest Data Route (Option B & C) ───────────────────
    async function loadBacktestData(universe) {
        const btStrip = document.getElementById('bt-stat-strip');
        const btChart = document.getElementById('bt-chart-container');
        const btBar = document.getElementById('bt-bar-chart-container');
        const btTbody = document.getElementById('bt-tbody');
        
        if (!btStrip || !btChart || !btBar || !btTbody) return;

        btStrip.innerHTML = `<div class="td-sub" style="padding:10px;">Syncing ledger metrics...</div>`;
        btChart.innerHTML = `<div class="loader-text" style="text-align:center; padding:60px 0;">Drawing wealth vectors...</div>`;
        btBar.innerHTML = `<div class="loader-text" style="text-align:center; padding:60px 0;">Syncing return metrics...</div>`;
        btTbody.innerHTML = `<tr><td colspan="6" class="td-sub" style="text-align:center; padding:40px 0;">Syncing quantitative archive...</td></tr>`;
        
        try {
            const res = await fetch(`${API_BASE}/api/backtest?universe=${universe}`);
            if (!res.ok) {
                let textErr = "Unable to fetch backtest logs";
                try {
                    const json = await res.json();
                    textErr = json.detail || textErr;
                } catch(e) {}
                throw new Error(textErr);
            }
            
            let data;
            try {
                data = await res.json();
            } catch (jsonErr) {
                throw new Error("Invalid response format received from backtest endpoint");
            }
            
            const stats = data.stats;
            const series = data.series;
            
            btStrip.innerHTML = `
                <div class="stat-cell">
                    <div class="stat-num">${(stats.ann_return * 100).toFixed(1)}%</div>
                    <div class="stat-key">Ann. L/S Return</div>
                </div>
                <div class="stat-cell">
                    <div class="stat-num">${(stats.ann_vol * 100).toFixed(1)}%</div>
                    <div class="stat-key">Ann. Volatility</div>
                </div>
                <div class="stat-cell">
                    <div class="stat-num"><em>${stats.sharpe ? stats.sharpe.toFixed(3) : 'N/A'}</em></div>
                    <div class="stat-key">Sharpe Ratio</div>
                </div>
                <div class="stat-cell">
                    <div class="stat-num">${(stats.max_drawdown * 100).toFixed(1)}%</div>
                    <div class="stat-key">Max Drawdown</div>
                </div>
                <div class="stat-cell">
                    <div class="stat-num">${(stats.hit_rate * 100).toFixed(1)}%</div>
                    <div class="stat-key">Quarterly Hit Rate</div>
                </div>
            `;
            
            btChart.innerHTML = drawBacktestLineChart(series);
            btBar.innerHTML = drawBacktestBarChart(series);
            
            let rowsHtml = '';
            series.slice().reverse().forEach(row => {
                const lsClass = row.ls_return > 0 ? 'td-good' : row.ls_return < 0 ? 'td-risk' : '';
                rowsHtml += `
                    <tr>
                        <td class="td-sub" style="font-weight: 600; color: var(--ink);">${row.quarter.substring(0,7)}</td>
                        <td>${(row.long_return * 100).toFixed(2)}%</td>
                        <td>${(row.short_return * 100).toFixed(2)}%</td>
                        <td class="${lsClass}" style="font-family: var(--mono); font-weight: bold;">${(row.ls_return * 100).toFixed(2)}%</td>
                        <td class="td-sub">${row.n_long}</td>
                        <td class="td-sub">${row.n_short}</td>
                    </tr>
                `;
            });
            btTbody.innerHTML = rowsHtml;
            
        } catch (err) {
            console.error(err);
            btStrip.innerHTML = `<div class="td-sub" style="color:var(--go); padding:10px;">Sync failed: ${err.message}</div>`;
            btChart.innerHTML = `<div class="td-sub" style="text-align:center; padding:40px;">Sync failed: ${err.message}</div>`;
            btBar.innerHTML = `<div class="td-sub" style="text-align:center; padding:40px;">Sync failed: ${err.message}</div>`;
            btTbody.innerHTML = `<tr><td colspan="6" class="td-sub" style="text-align:center; padding:40px 0; color:var(--go);">Failed to sync quantitative archive.</td></tr>`;
        }
    }

    // ── DOM Listeners & Initialization ──────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', () => {
        // Universal View Toggling Setup
        document.addEventListener('click', e => {
            // Check data-view targets
            const vBtn = e.target.closest('[data-view]');
            if (vBtn) {
                e.preventDefault();
                setView(vBtn.getAttribute('data-view'), true);
                return;
            }
            
            // Check data-scroll-to targets
            const sBtn = e.target.closest('[data-scroll-to]');
            if (sBtn) {
                e.preventDefault();
                const targetEl = document.getElementById(sBtn.getAttribute('data-scroll-to'));
                if (targetEl) targetEl.scrollIntoView({ behavior: 'smooth' });
                return;
            }
            
            // Check data-scroll links
            const scrollL = e.target.closest('a[data-scroll]');
            if (scrollL) {
                e.preventDefault();
                const targetId = scrollL.getAttribute('href').replace('#', '');
                const targetEl = document.getElementById(targetId);
                if (targetEl) targetEl.scrollIntoView({ behavior: 'smooth' });
            }
        });

        // ── Caligula Sub-view listeners ──────────────────────────────────────────
        const subbtnRanksEl = document.getElementById('subbtn-rankings');
        const subbtnBacktestEl = document.getElementById('subbtn-backtest');
        
        if (subbtnRanksEl) {
            subbtnRanksEl.addEventListener('click', () => setCaligulaSubview('rankings'));
        }
        if (subbtnBacktestEl) {
            subbtnBacktestEl.addEventListener('click', () => setCaligulaSubview('backtest'));
        }

        // Toggle backtest portfolios dynamically (Segment Controls)
        const btnEp = document.getElementById('bt-toggle-ep');
        const btnGc = document.getElementById('bt-toggle-gc');
        
        if (btnEp && btnGc) {
            btnEp.addEventListener('click', () => {
                btnEp.style.background = "var(--ink)";
                btnEp.style.color = "var(--p)";
                btnGc.style.background = "transparent";
                btnGc.style.color = "var(--ink)";
                loadBacktestData('ep_study');
            });
            
            btnGc.addEventListener('click', () => {
                btnGc.style.background = "var(--ink)";
                btnGc.style.color = "var(--p)";
                btnEp.style.background = "transparent";
                btnEp.style.color = "var(--ink)";
                loadBacktestData('general_corp');
            });
        }

        // Search inputs
        const searchInput = document.getElementById('ticker-input');
        const searchBtn = document.getElementById('search-trigger-btn');

        function executeSearch() {
            const sym = searchInput.value;
            if (sym) runDiligenceAnalysis(sym);
        }

        if (searchBtn) {
            searchBtn.addEventListener('click', executeSearch);
        }
        if (searchInput) {
            searchInput.addEventListener('keypress', e => {
                if (e.key === 'Enter') executeSearch();
            });
        }

        // Return button from Deep dive
        const ddBackBtn = document.getElementById('dd-back-btn');
        if (ddBackBtn) {
            ddBackBtn.addEventListener('click', () => {
                setCaligulaSubview('rankings');
                if (searchInput) searchInput.value = '';
            });
        }

        // Handle URL hashes on entry
        window.addEventListener('popstate', fromHash);
        fromHash();
    });

})();
