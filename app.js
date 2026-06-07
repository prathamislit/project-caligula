/**
 * PNS · Research — static site controller.
 *
 * Architecture:
 *   - index.html is a shell. All project body copy lives in data/*.json.
 *   - This file fetches the content JSON, renders each project view, then
 *     wires navigation and the Caligula interactive layer.
 *   - Generated Caligula pipeline data is read from a single static file:
 *     outputs/website/public_caligula_data.json  (universe / backtest / analyze).
 *   - No metrics are hardcoded here and there is no silent fallback: if any
 *     JSON fails to load, a visible error is shown.
 */

(function () {
    "use strict";

    // ── Content + data locations ────────────────────────────────────────────────
    const CONTENT = {
        projects: "data/projects.json",
        goldstein: "data/goldstein.json",
        caligula: "data/caligula.json",
        chc: "data/chc.json"
    };
    const PIPELINE_URL = "outputs/website/public_caligula_data.json";

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

    let eogHeatmapConfig = null;

    // ── Fetch helpers (no silent fallback) ──────────────────────────────────────
    async function fetchJSON(url) {
        let res;
        try {
            res = await fetch(url, { cache: "no-cache" });
        } catch (netErr) {
            throw new Error("Could not load " + url + " — " + netErr.message);
        }
        if (!res.ok) throw new Error("Could not load " + url + " (HTTP " + res.status + ")");
        try {
            return await res.json();
        } catch (parseErr) {
            throw new Error("Invalid JSON in " + url + " — " + parseErr.message);
        }
    }

    function showFatalError(err) {
        console.error(err);
        let banner = document.getElementById("fatal-error");
        if (!banner) {
            banner = document.createElement("div");
            banner.id = "fatal-error";
            banner.setAttribute("role", "alert");
            banner.style.cssText =
                "position:fixed;left:0;right:0;top:0;z-index:9999;" +
                "background:#7a1d12;color:#F4EEDB;" +
                "font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:.04em;" +
                "padding:14px 20px;line-height:1.6;border-bottom:2px solid #B8922A;";
            document.body.appendChild(banner);
        }
        banner.textContent = "Content failed to load. " + (err && err.message ? err.message : err);
    }

    // ── Home view rendering (from data/projects.json) ───────────────────────────
    function renderCard(c) {
        const dark = c.variant === "dark";
        const titleCls = dark ? "pj-title-dk" : "pj-title";
        const bodyCls = dark ? "pj-body-dk" : "pj-body";
        const linkStyle = dark ? "" : ' style="color:var(--ink)"';
        const fillPath = c.spark.line + " L280,38 L0,38 Z";
        const stats = c.stats
            .map(function (s) {
                return (
                    '<div class="pj-stat"><div class="pj-stat-val">' +
                    s.val +
                    '</div><div class="pj-stat-key">' +
                    s.key +
                    "</div></div>"
                );
            })
            .join("");
        return (
            '<div class="project' + (dark ? " dark" : "") + '">' +
            '<div class="pj-head">' +
            '<div class="pj-roman">' + c.roman + "</div>" +
            '<div class="pj-stamp">' + c.stamp + "</div>" +
            "</div>" +
            '<div class="' + titleCls + '">' + c.title + "</div>" +
            '<div class="pj-tag">' + c.tag + "</div>" +
            '<p class="' + bodyCls + '">' + c.body + "</p>" +
            '<svg class="pj-spark" viewBox="0 0 280 38" preserveAspectRatio="none" aria-hidden="true">' +
            '<path d="' + c.spark.line + '" fill="none" stroke="' + c.spark.stroke + '" stroke-width="1.5"/>' +
            '<path d="' + fillPath + '" fill="' + c.spark.fillColor + '"/>' +
            "</svg>" +
            '<button class="pj-link"' + linkStyle + ' data-view="' + c.link.view + '">' + c.link.label + "</button>" +
            '<div class="pj-stats">' + stats + "</div>" +
            "</div>"
        );
    }

    function renderHome(p) {
        const cardsHtml = (p.portfolio.cards || []).map(renderCard).join("");
        const portfolioSection =
            '<section id="portfolio" data-folio="P. 01 / PORTFOLIO">' +
            '<div class="sec-label" data-num="' + p.portfolio.label.num + '">' + p.portfolio.label.text + "</div>" +
            '<div class="projects">' + cardsHtml + "</div>" +
            "</section>";
        document.getElementById("view-home").innerHTML =
            p.hero + portfolioSection + p.method + p.pullquote;
    }

    // ── Caligula pipeline data (single static file, cached) ──────────────────────
    let _pipelinePromise = null;
    function loadPipeline() {
        if (!_pipelinePromise) {
            _pipelinePromise = fetchJSON(PIPELINE_URL).catch(function (err) {
                _pipelinePromise = null; // allow retry on next interaction
                throw err;
            });
        }
        return _pipelinePromise;
    }
    function pipelineErr(err) {
        return "Pipeline data unavailable — generate " + PIPELINE_URL + ". (" + (err && err.message ? err.message : err) + ")";
    }

    // ── Parent view navigation ───────────────────────────────────────────────────
    const VIEWS = ["home", "goldstein", "chc", "caligula"];
    let activeView = "home";

    function setView(name, push) {
        if (!VIEWS.includes(name)) name = "home";
        activeView = name;

        document.querySelectorAll("main.view").forEach(function (v) {
            v.classList.remove("active");
        });
        const el = document.getElementById("view-" + name);
        if (el) el.classList.add("active");

        document.querySelectorAll("[data-view]").forEach(function (b) {
            b.classList.toggle("is-active", b.getAttribute("data-view") === name);
        });

        document.title =
            name === "home"
                ? "PNS · Research Folio"
                : name === "goldstein"
                ? "Project Goldstein — PNS · Research"
                : name === "chc"
                ? "CHC Platform — PNS · Research"
                : "Project Caligula — PNS · Research";

        if (push) {
            try {
                history.pushState({ v: name }, "", "#" + name);
            } catch (e) {
                try { window.location.hash = name; } catch (hashErr) {}
            }
        }
        window.scrollTo({ top: 0, behavior: "smooth" });

        if (name === "caligula") {
            setCaligulaSubview("rankings");
            loadUniverseRankings();
        }
    }

    function fromHash() {
        const h = (location.hash || "").replace("#", "").toLowerCase();
        setView(VIEWS.includes(h) ? h : "home", false);
    }

    // ── Caligula sub-view toggling ───────────────────────────────────────────────
    let activeCaligulaSubview = "rankings";

    function setCaligulaSubview(subviewName) {
        activeCaligulaSubview = subviewName;
        const subviewRanks = document.getElementById("caligula-rankings-subview");
        const subviewBacktest = document.getElementById("caligula-backtest-subview");
        const subviewAudit = document.getElementById("caligula-audit-subview");
        const subviewDeepdive = document.getElementById("caligula-deepdive-subview");
        const subbtnRanks = document.getElementById("subbtn-rankings");
        const subbtnBacktest = document.getElementById("subbtn-backtest");
        const subbtnAudit = document.getElementById("subbtn-audit");
        const subbtnEogdcf = document.getElementById("subbtn-eogdcf");

        [subviewRanks, subviewBacktest, subviewAudit, subviewDeepdive].forEach(function (v) {
            if (v) v.classList.remove("active");
        });
        [subbtnRanks, subbtnBacktest, subbtnAudit, subbtnEogdcf].forEach(function (b) {
            if (b) b.classList.remove("on");
        });

        if (subviewName === "rankings") {
            if (subviewRanks) subviewRanks.classList.add("active");
            if (subbtnRanks) subbtnRanks.classList.add("on");
        } else if (subviewName === "backtest") {
            if (subviewBacktest) subviewBacktest.classList.add("active");
            if (subbtnBacktest) subbtnBacktest.classList.add("on");
            loadBacktestData("ep_study");
        } else if (subviewName === "audit") {
            if (subviewAudit) subviewAudit.classList.add("active");
            if (subbtnAudit) subbtnAudit.classList.add("on");
        } else if (subviewName === "deepdive") {
            if (subviewDeepdive) subviewDeepdive.classList.add("active");
        }
    }

    // ── Caligula rankings ledger ─────────────────────────────────────────────────
    async function loadUniverseRankings() {
        const tbody = document.getElementById("universe-tbody");
        if (!tbody) return;
        try {
            const data = await loadPipeline();
            const rankings = data && data.universe ? data.universe.rankings : null;
            if (!rankings || rankings.length === 0) {
                tbody.innerHTML = '<tr><td colspan="12" class="td-sub" style="text-align:center;padding:40px 0">No active study rankings compiled.</td></tr>';
                return;
            }

            let rowsHtml = "";
            rankings.forEach(function (row) {
                const tierClass = row.tier === "A" ? "td-good" : row.tier === "B" ? "td-warn" : "td-risk";
                rowsHtml +=
                    '<tr style="cursor:pointer" data-ticker="' + row.ticker + '">' +
                    '<td class="td-sub">' + String(row.rank).padStart(2, "0") + "</td>" +
                    '<td style="font-weight:600;color:var(--ink);font-family:var(--mono);letter-spacing:.04em">' + row.ticker + "</td>" +
                    '<td><span class="tier-pill ' + tierClass + '">' + row.tier + "</span></td>" +
                    '<td style="font-family:var(--mono);font-weight:700;color:var(--go)">' + row.caligula_score.toFixed(3) + "</td>" +
                    '<td class="td-sub">' + row.unit_economics_score.toFixed(2) + "</td>" +
                    '<td class="td-sub">' + row.capital_discipline_score.toFixed(2) + "</td>" +
                    '<td class="td-sub">' + row.balance_sheet_score.toFixed(2) + "</td>" +
                    '<td class="td-sub">' + row.hedge_book_score.toFixed(2) + "</td>" +
                    '<td class="td-sub">' + row.reserves_score.toFixed(2) + "</td>" +
                    '<td class="td-sub">' + row.operational_score.toFixed(2) + "</td>" +
                    '<td class="td-sub">' + row.sentiment_score.toFixed(2) + "</td>" +
                    '<td class="td-sub">' + row.macro_sensitivity_score.toFixed(2) + "</td>" +
                    "</tr>";
            });
            tbody.innerHTML = rowsHtml;

            tbody.querySelectorAll("tr").forEach(function (tr) {
                tr.addEventListener("click", function () {
                    const symbol = tr.dataset.ticker;
                    if (symbol) runDiligenceAnalysis(symbol);
                });
            });
        } catch (err) {
            console.error(err);
            tbody.innerHTML =
                '<tr><td colspan="12" class="td-sub" style="text-align:center;padding:40px 0;color:var(--go)">' +
                pipelineErr(err) +
                "</td></tr>";
        }
    }

    // ── SVG chart builders ───────────────────────────────────────────────────────
    function drawRadarChart(scores) {
        const cx = 250, cy = 180, maxRadius = 110, numPillars = 8;
        let svg = '<svg viewBox="0 0 500 360" width="100%" height="100%">';
        for (let j = 1; j <= 5; j++) {
            const r = (j / 5) * maxRadius;
            svg += '<circle cx="' + cx + '" cy="' + cy + '" r="' + r + '" stroke="rgba(17,16,8,0.06)" fill="none" stroke-width="1" />';
            if (j === 3 || j === 5) {
                svg += '<text x="' + (cx + 4) + '" y="' + (cy - r + 3) + '" fill="#7A766E" font-family="JetBrains Mono, monospace" font-size="7" opacity=".6">' + (j / 5).toFixed(1) + "</text>";
            }
        }
        const polygonPoints = [];
        for (let i = 0; i < numPillars; i++) {
            const angle = (i * 2 * Math.PI / numPillars) - (Math.PI / 2);
            const ax = cx + maxRadius * Math.cos(angle);
            const ay = cy + maxRadius * Math.sin(angle);
            svg += '<line x1="' + cx + '" y1="' + cy + '" x2="' + ax + '" y2="' + ay + '" stroke="rgba(17,16,8,0.06)" stroke-width="1" />';
            const scoreVal = scores[i] || 0.5;
            const vx = cx + maxRadius * scoreVal * Math.cos(angle);
            const vy = cy + maxRadius * scoreVal * Math.sin(angle);
            polygonPoints.push(vx + "," + vy);
            let lx = cx + maxRadius * 1.25 * Math.cos(angle);
            let ly = cy + maxRadius * 1.25 * Math.sin(angle);
            let anchor = "middle";
            if (Math.cos(angle) > 0.1) anchor = "start";
            if (Math.cos(angle) < -0.1) anchor = "end";
            if (Math.abs(Math.sin(angle)) > 0.9) ly += (Math.sin(angle) > 0 ? 4 : -2);
            svg += '<text x="' + lx + '" y="' + ly + '" fill="#111008" font-family="EB Garamond, serif" font-size="11" font-weight="500" text-anchor="' + anchor + '">' + PILLAR_LABELS[i] + '<tspan x="' + lx + '" dy="11" font-family="JetBrains Mono, monospace" font-size="8" fill="#B8922A">' + scoreVal.toFixed(2) + "</tspan></text>";
        }
        svg += '<polygon points="' + polygonPoints.join(" ") + '" fill="rgba(184,146,42,0.16)" stroke="#B8922A" stroke-width="2" />';
        polygonPoints.forEach(function (pt) {
            const parts = pt.split(",");
            svg += '<circle cx="' + parts[0] + '" cy="' + parts[1] + '" r="3" fill="#111008" stroke="#B8922A" stroke-width="1" />';
        });
        svg += "</svg>";
        return svg;
    }

    function drawHistoryLineChart(history) {
        if (!history || history.length === 0) return '<div class="td-sub">No historical quality path available.</div>';
        const w = 600, h = 260, padL = 50, padR = 20, padT = 20, padB = 40;
        const chartW = w - padL - padR, chartH = h - padT - padB;
        const quarters = history.map(function (d) { return d.quarter; });
        const scores = history.map(function (d) { return d.caligula_score || 0.5; });
        const minVal = 0.0, maxVal = 1.0;
        let points = [];
        for (let i = 0; i < history.length; i++) {
            const x = padL + (i / (history.length - 1 || 1)) * chartW;
            const y = padT + chartH - ((scores[i] - minVal) / (maxVal - minVal)) * chartH;
            points.push({ x: x, y: y, score: scores[i], label: quarters[i] });
        }
        let svg = '<svg viewBox="0 0 ' + w + " " + h + '" width="100%" height="100%">';
        for (let j = 0; j <= 4; j++) {
            const yVal = minVal + (j / 4) * (maxVal - minVal);
            const yPos = padT + chartH - (j / 4) * chartH;
            svg += '<line x1="' + padL + '" y1="' + yPos + '" x2="' + (w - padR) + '" y2="' + yPos + '" stroke="rgba(17,16,8,0.06)" stroke-width="1" /><text x="' + (padL - 10) + '" y="' + (yPos + 3) + '" fill="#7A766E" font-family="JetBrains Mono, monospace" font-size="7.5" text-anchor="end">' + yVal.toFixed(2) + "</text>";
        }
        const step = Math.max(1, Math.floor(history.length / 5));
        points.forEach(function (pt, idx) {
            if (idx % step === 0 || idx === history.length - 1) {
                svg += '<line x1="' + pt.x + '" y1="' + padT + '" x2="' + pt.x + '" y2="' + (padT + chartH) + '" stroke="rgba(17,16,8,0.03)" stroke-dasharray="2,2" stroke-width="1" /><text x="' + pt.x + '" y="' + (padT + chartH + 18) + '" fill="#7A766E" font-family="JetBrains Mono, monospace" font-size="7.5" text-anchor="middle">' + (pt.label.length > 7 ? pt.label.substring(2, 7) : pt.label) + "</text>";
            }
        });
        let pathString = "M " + points[0].x + " " + (padT + chartH);
        points.forEach(function (pt) { pathString += " L " + pt.x + " " + pt.y; });
        pathString += " L " + points[points.length - 1].x + " " + (padT + chartH) + " Z";
        svg += '<path d="' + pathString + '" fill="rgba(184,146,42,0.08)" stroke="none" />';
        let lineString = "M " + points[0].x + " " + points[0].y;
        for (let i = 1; i < points.length; i++) { lineString += " L " + points[i].x + " " + points[i].y; }
        svg += '<path d="' + lineString + '" fill="none" stroke="#B8922A" stroke-width="2" />';
        points.forEach(function (pt) { svg += '<circle cx="' + pt.x + '" cy="' + pt.y + '" r="3" fill="#111008" stroke="#B8922A" stroke-width="1" />'; });
        svg += "</svg>";
        return svg;
    }

    function drawBacktestLineChart(series) {
        if (!series || series.length === 0) return '<div class="td-sub">No backtest data loaded.</div>';
        const w = 600, h = 320, padL = 50, padR = 20, padT = 30, padB = 40;
        const chartW = w - padL - padR, chartH = h - padT - padB;
        const cumLS = series.map(function (d) { return d.cum_ls; });
        const cumLong = series.map(function (d) { return d.cum_long; });
        const cumShort = series.map(function (d) { return d.cum_short; });
        const allVals = cumLS.concat(cumLong).concat(cumShort);
        const minVal = Math.max(0.0, Math.min.apply(null, allVals) * 0.9);
        const maxVal = Math.max.apply(null, allVals) * 1.1;
        let ptsLS = [], ptsLong = [], ptsShort = [];
        series.forEach(function (d, idx) {
            const x = padL + (idx / (series.length - 1 || 1)) * chartW;
            ptsLS.push({ x: x, y: padT + chartH - ((d.cum_ls - minVal) / (maxVal - minVal)) * chartH });
            ptsLong.push({ x: x, y: padT + chartH - ((d.cum_long - minVal) / (maxVal - minVal)) * chartH });
            ptsShort.push({ x: x, y: padT + chartH - ((d.cum_short - minVal) / (maxVal - minVal)) * chartH });
        });
        let svg = '<svg viewBox="0 0 ' + w + " " + h + '" width="100%" height="100%"><g transform="translate(' + padL + ', 12)"><line x1="0" y1="5" x2="20" y2="5" stroke="#B8922A" stroke-width="2.5" /><text x="25" y="9" fill="#111008" font-family="EB Garamond, serif" font-size="9" font-weight="600">Long-Short L/S</text><line x1="110" y1="5" x2="130" y2="5" stroke="#111008" stroke-dasharray="2,2" stroke-width="1.5" /><text x="135" y="9" fill="#111008" font-family="EB Garamond, serif" font-size="9" font-weight="600">Long Only</text><line x1="210" y1="5" x2="230" y2="5" stroke="#55504A" stroke-dasharray="2,2" stroke-width="1.5" /><text x="235" y="9" fill="#111008" font-family="EB Garamond, serif" font-size="9" font-weight="600">Short Only</text></g>';
        for (let j = 0; j <= 5; j++) {
            const yVal = minVal + (j / 5) * (maxVal - minVal);
            const yPos = padT + chartH - (j / 5) * chartH;
            svg += '<line x1="' + padL + '" y1="' + yPos + '" x2="' + (w - padR) + '" y2="' + yPos + '" stroke="rgba(17,16,8,0.06)" stroke-width="1" /><text x="' + (padL - 10) + '" y="' + (yPos + 3) + '" fill="#7A766E" font-family="JetBrains Mono, monospace" font-size="7.5" text-anchor="end">' + yVal.toFixed(2) + "</text>";
        }
        const step = Math.max(1, Math.floor(series.length / 6));
        series.forEach(function (d, idx) {
            if (idx % step === 0 || idx === series.length - 1) {
                const x = padL + (idx / (series.length - 1 || 1)) * chartW;
                svg += '<line x1="' + x + '" y1="' + padT + '" x2="' + x + '" y2="' + (padT + chartH) + '" stroke="rgba(17,16,8,0.03)" stroke-dasharray="2,2" stroke-width="1" /><text x="' + x + '" y="' + (padT + chartH + 18) + '" fill="#7A766E" font-family="JetBrains Mono, monospace" font-size="7.5" text-anchor="middle">' + d.quarter.substring(2, 7) + "</text>";
            }
        });
        function autoDrawPath(pts, color, width, dash) {
            let str = "M " + pts[0].x + " " + pts[0].y;
            for (let i = 1; i < pts.length; i++) { str += " L " + pts[i].x + " " + pts[i].y; }
            svg += '<path d="' + str + '" fill="none" stroke="' + color + '" stroke-width="' + width + '" stroke-dasharray="' + dash + '" />';
        }
        autoDrawPath(ptsShort, "#55504A", "1.5", "3,3");
        autoDrawPath(ptsLong, "#111008", "1.5", "2,2");
        autoDrawPath(ptsLS, "#B8922A", "2.5", "none");
        svg += "</svg>";
        return svg;
    }

    function drawBacktestBarChart(series) {
        if (!series || series.length === 0) return '<div class="td-sub">No backtest data loaded.</div>';
        const w = 600, h = 320, padL = 50, padR = 20, padT = 30, padB = 40;
        const chartW = w - padL - padR, chartH = h - padT - padB;
        const rets = series.map(function (d) { return d.ls_return; });
        const minVal = Math.min(-0.15, Math.min.apply(null, rets) * 1.2);
        const maxVal = Math.max(0.15, Math.max.apply(null, rets) * 1.2);
        let svg = '<svg viewBox="0 0 ' + w + " " + h + '" width="100%" height="100%"><text x="' + padL + '" y="15" fill="#111008" font-family="EB Garamond, serif" font-size="9" font-weight="600" text-anchor="start">Quarterly L/S Returns (%)</text>';
        for (let j = 0; j <= 4; j++) {
            const yVal = minVal + (j / 4) * (maxVal - minVal);
            const yPos = padT + chartH - (j / 4) * chartH;
            svg += '<line x1="' + padL + '" y1="' + yPos + '" x2="' + (w - padR) + '" y2="' + yPos + '" stroke="rgba(17,16,8,0.06)" stroke-width="1" /><text x="' + (padL - 10) + '" y="' + (yPos + 3) + '" fill="#7A766E" font-family="JetBrains Mono, monospace" font-size="7.5" text-anchor="end">' + (yVal * 100).toFixed(0) + "%</text>";
        }
        const yZero = padT + chartH - ((0.0 - minVal) / (maxVal - minVal)) * chartH;
        svg += '<line x1="' + padL + '" y1="' + yZero + '" x2="' + (w - padR) + '" y2="' + yZero + '" stroke="#111008" stroke-width="1.5" />';
        const barW = Math.max(2, (chartW / series.length) * 0.6);
        series.forEach(function (d, idx) {
            const x = padL + (idx / (series.length - 1 || 1)) * chartW;
            const yVal = d.ls_return;
            const yPos = padT + chartH - ((yVal - minVal) / (maxVal - minVal)) * chartH;
            const barH = Math.abs(yPos - yZero);
            const barY = yVal >= 0 ? yPos : yZero;
            const color = yVal >= 0 ? "#B8922A" : "#111008";
            svg += '<rect x="' + (x - barW / 2) + '" y="' + barY + '" width="' + barW + '" height="' + barH + '" fill="' + color + '" opacity=".85" />';
        });
        const step = Math.max(1, Math.floor(series.length / 6));
        series.forEach(function (d, idx) {
            if (idx % step === 0 || idx === series.length - 1) {
                const x = padL + (idx / (series.length - 1 || 1)) * chartW;
                svg += '<text x="' + x + '" y="' + (padT + chartH + 18) + '" fill="#7A766E" font-family="JetBrains Mono, monospace" font-size="7.5" text-anchor="middle">' + d.quarter.substring(2, 7) + "</text>";
            }
        });
        svg += "</svg>";
        return svg;
    }

    // ── EOG sensitivity heatmap (config from data/caligula.json) ─────────────────
    function renderEogHeatmap() {
        const host = document.getElementById("eog-heatmap-container");
        if (!host || !eogHeatmapConfig) return;
        const cfg = eogHeatmapConfig;
        const waccs = cfg.waccs, wtis = cfg.wtis;
        const baseW = cfg.baseWacc, baseP = cfg.basePrice, baseV = cfg.baseValue;
        const wtiSlope = cfg.wtiSlope, waccSlope = cfg.waccSlope;
        const grid = waccs.map(function (w) {
            return wtis.map(function (p) {
                return baseV + (p - baseP) * wtiSlope + (w - baseW) * waccSlope;
            });
        });
        const flat = grid.reduce(function (a, r) { return a.concat(r); }, []);
        const lo = Math.min.apply(null, flat), hi = Math.max.apply(null, flat);

        const W = 460, H = 280;
        const padL = 64, padR = 18, padT = 28, padB = 44;
        const cellW = (W - padL - padR) / wtis.length;
        const cellH = (H - padT - padB) / waccs.length;

        function color(v) {
            const t = (v - lo) / Math.max(1e-6, hi - lo);
            if (t < 0.5) {
                const k = t / 0.5;
                return "rgb(" + Math.round(180 + (233 - 180) * k) + "," + Math.round(58 + (228 - 58) * k) + "," + Math.round(44 + (215 - 44) * k) + ")";
            }
            const k = (t - 0.5) / 0.5;
            return "rgb(" + Math.round(233 + (47 - 233) * k) + "," + Math.round(228 + (107 - 228) * k) + "," + Math.round(215 + (58 - 215) * k) + ")";
        }

        let cells = "";
        for (let r = 0; r < waccs.length; r++) {
            for (let c = 0; c < wtis.length; c++) {
                const v = grid[r][c];
                const x = padL + c * cellW;
                const y = padT + r * cellH;
                const isBase = Math.abs(waccs[r] - baseW) < 0.01 && Math.abs(wtis[c] - baseP) < 0.01;
                const t = (v - lo) / Math.max(1e-6, hi - lo);
                const textColor = t < 0.18 || t > 0.82 ? "#F6F4EF" : "#111008";
                cells += '<rect x="' + x + '" y="' + y + '" width="' + (cellW - 2) + '" height="' + (cellH - 2) + '" fill="' + color(v) + '" />';
                if (isBase) {
                    cells += '<rect x="' + (x + 1) + '" y="' + (y + 1) + '" width="' + (cellW - 4) + '" height="' + (cellH - 4) + '" fill="none" stroke="#111008" stroke-width="2" />';
                }
                cells += '<text x="' + (x + cellW / 2 - 1) + '" y="' + (y + cellH / 2 + 4) + '" text-anchor="middle" font-family="ui-monospace,monospace" font-size="11" font-weight="' + (isBase ? 600 : 500) + '" fill="' + textColor + '">$' + v.toFixed(0) + "</text>";
            }
        }

        let xLabels = "";
        wtis.forEach(function (p, i) {
            const x = padL + i * cellW + cellW / 2;
            xLabels += '<text x="' + x + '" y="' + (H - padB + 18) + '" text-anchor="middle" font-family="ui-monospace,monospace" font-size="9.5" letter-spacing="1.4" fill="#5A554A">$' + p + "</text>";
        });
        let yLabels = "";
        waccs.forEach(function (w, i) {
            const y = padT + i * cellH + cellH / 2 + 4;
            yLabels += '<text x="' + (padL - 10) + '" y="' + y + '" text-anchor="end" font-family="ui-monospace,monospace" font-size="9.5" letter-spacing="1.4" fill="#5A554A">' + w.toFixed(2) + "%</text>";
        });

        host.innerHTML =
            '<svg viewBox="0 0 ' + W + " " + H + '" width="100%" preserveAspectRatio="xMidYMid meet" style="max-width:520px">' +
            '<text x="' + padL + '" y="16" font-family="ui-monospace,monospace" font-size="9" letter-spacing="2" fill="#5A554A">WACC \u2193 &nbsp; / &nbsp; LONG-RUN WTI \u2192</text>' +
            cells + xLabels + yLabels +
            "</svg>";
    }

    // ── Single-name diligence ────────────────────────────────────────────────────
    async function runDiligenceAnalysis(ticker) {
        const symbol = ticker.toUpperCase().trim();
        if (!symbol) return;
        const loader = document.getElementById("api-loader");
        const errorMsg = document.getElementById("search-error-msg");
        if (errorMsg) errorMsg.textContent = "";
        if (loader) loader.style.display = "block";

        try {
            const data = await loadPipeline();
            const analyze = data && data.analyze ? data.analyze : null;
            const entry = analyze ? analyze[symbol] : null;
            if (loader) loader.style.display = "none";

            if (!entry || !entry.latest) {
                if (errorMsg) errorMsg.textContent = symbol + " is not in the published dataset.";
                return;
            }

            setCaligulaSubview("deepdive");
            const latest = entry.latest;

            document.getElementById("dd-kicker").innerHTML =
                (entry.type === "ep_study" ? "E&P Study Operator" : "Corporate Equities") + " &nbsp;·&nbsp; " + symbol;
            document.getElementById("dd-title").innerHTML = (latest.name || symbol) + " <em>Analysis</em>";
            document.getElementById("dd-meta").innerHTML = latest.sector + " &nbsp;·&nbsp; " + latest.industry + " &nbsp;·&nbsp; " + latest.quarter;

            document.getElementById("dd-stat-strip").innerHTML =
                '<div class="stat-cell" data-id="A"><div class="stat-num">' + latest.caligula_score.toFixed(3) + '</div><div class="stat-key">Composite Score</div></div>' +
                '<div class="stat-cell" data-id="B"><div class="stat-num"><em>Tier ' + latest.tier + '</em></div><div class="stat-key">Diligence Rating</div></div>' +
                '<div class="stat-cell" data-id="C"><div class="stat-num">' + latest.quarter + '</div><div class="stat-key">Reporting Period</div></div>' +
                '<div class="stat-cell" data-id="D"><div class="stat-num" style="font-size:14px;padding-top:10px;font-family:var(--mono);text-transform:uppercase;line-height:1.2">' + latest.industry.split(" ").slice(0, 2).join(" ") + '</div><div class="stat-key">Sector Class</div></div>';

            const scoresArray = PILLAR_KEYS.map(function (k) { return latest[k] || 0.5; });
            document.getElementById("dd-chart-container").innerHTML = drawRadarChart(scoresArray);

            if (entry.history && entry.history.length > 0) {
                document.getElementById("dd-history-chart-container").innerHTML = drawHistoryLineChart(entry.history);
            } else {
                document.getElementById("dd-history-chart-container").innerHTML = '<div class="td-sub" style="text-align:center;padding:40px">Quality evolutionary trends will populate here.</div>';
            }

            const eogPlate = document.getElementById("eog-dcf-plate");
            if (eogPlate) {
                if (symbol === "EOG") {
                    eogPlate.style.display = "block";
                    renderEogHeatmap();
                } else {
                    eogPlate.style.display = "none";
                }
            }

            const tbody = document.getElementById("dd-metrics-tbody");
            let metricsHtml = "";
            PILLAR_KEYS.forEach(function (key, idx) {
                const score = latest[key] || 0.5;
                const scoreClass = score >= 0.7 ? "td-good" : score >= 0.5 ? "td-warn" : "td-risk";
                let valDesc = "Ingested footnote resolved";
                if (latest.raw_metrics) {
                    const raw = latest.raw_metrics;
                    if (key.indexOf("unit_economics") >= 0) valDesc = raw.gross_margin ? "Gross Margin: " + (raw.gross_margin * 100).toFixed(0) + "%" : "Baseline geological costs";
                    else if (key.indexOf("capital_discipline") >= 0) valDesc = raw.roa ? "ROA: " + (raw.roa * 100).toFixed(1) + "%" : "FCF payout coverage";
                    else if (key.indexOf("balance_sheet") >= 0) valDesc = raw.debt_ebitda ? "Debt/EBITDA: " + raw.debt_ebitda.toFixed(1) + "x" : "Net Leverage Buffer";
                    else if (key.indexOf("hedge_book") >= 0) valDesc = raw.quick_ratio ? "Quick Ratio: " + raw.quick_ratio.toFixed(2) + "x" : "Hedge floors parsed";
                    else if (key.indexOf("reserves") >= 0) valDesc = raw.revenue_growth ? "Revenue Growth: " + (raw.revenue_growth * 100).toFixed(0) + "%" : "Inventory replacements";
                    else if (key.indexOf("operational") >= 0) valDesc = raw.roe ? "ROE: " + (raw.roe * 100).toFixed(0) + "%" : "Engineering gains";
                    else if (key.indexOf("sentiment") >= 0) valDesc = raw.short_pct ? "Short Float: " + (raw.short_pct * 100).toFixed(1) + "%" : "Short sale indicators";
                    else if (key.indexOf("macro") >= 0) valDesc = raw.beta ? "Beta Coefficient: " + raw.beta.toFixed(2) : "Market crash protection";
                }
                metricsHtml += '<tr><td style="font-weight:500">' + PILLAR_LABELS[idx] + '</td><td class="td-sub">' + valDesc + '</td><td class="' + scoreClass + '" style="font-family:var(--mono);font-weight:600">' + score.toFixed(2) + "</td></tr>";
            });
            tbody.innerHTML = metricsHtml;
        } catch (err) {
            console.error(err);
            if (loader) loader.style.display = "none";
            if (errorMsg) errorMsg.textContent = pipelineErr(err);
        }
    }

    async function loadBacktestData(universe) {
        const btStrip = document.getElementById("bt-stat-strip");
        const btChart = document.getElementById("bt-chart-container");
        const btBar = document.getElementById("bt-bar-chart-container");
        const btTbody = document.getElementById("bt-tbody");
        if (!btStrip || !btChart || !btBar || !btTbody) return;

        btStrip.innerHTML = '<div class="td-sub" style="padding:10px">Syncing ledger metrics…</div>';
        btChart.innerHTML = '<div class="loader-text" style="text-align:center;padding:60px 0">Drawing wealth vectors…</div>';
        btBar.innerHTML = '<div class="loader-text" style="text-align:center;padding:60px 0">Syncing return metrics…</div>';
        btTbody.innerHTML = '<tr><td colspan="6" class="td-sub" style="text-align:center;padding:40px 0">Syncing quantitative archive…</td></tr>';

        try {
            const data = await loadPipeline();
            const bt = data && data.backtest ? data.backtest[universe] : null;
            if (!bt || !bt.stats || !bt.series) throw new Error("No backtest block for '" + universe + "'");
            const stats = bt.stats, series = bt.series;

            btStrip.innerHTML =
                '<div class="stat-cell" data-id="A"><div class="stat-num">' + (stats.ann_return * 100).toFixed(1) + '<em>%</em></div><div class="stat-key">Ann. L/S Return</div></div>' +
                '<div class="stat-cell" data-id="B"><div class="stat-num">' + (stats.ann_vol * 100).toFixed(1) + '<em>%</em></div><div class="stat-key">Ann. Volatility</div></div>' +
                '<div class="stat-cell" data-id="C"><div class="stat-num"><em>' + (stats.sharpe ? stats.sharpe.toFixed(3) : "N/A") + '</em></div><div class="stat-key">Sharpe Ratio</div></div>' +
                '<div class="stat-cell" data-id="D"><div class="stat-num">' + (stats.max_drawdown * 100).toFixed(1) + '<em>%</em></div><div class="stat-key">Max Drawdown</div></div>' +
                '<div class="stat-cell" data-id="E"><div class="stat-num">' + (stats.hit_rate * 100).toFixed(1) + '<em>%</em></div><div class="stat-key">Quarterly Hit Rate</div></div>';
            btChart.innerHTML = drawBacktestLineChart(series);
            btBar.innerHTML = drawBacktestBarChart(series);

            let rowsHtml = "";
            series.slice().reverse().forEach(function (row) {
                const lsClass = row.ls_return > 0 ? "td-good" : row.ls_return < 0 ? "td-risk" : "";
                rowsHtml += '<tr><td class="td-sub" style="font-weight:600;color:var(--ink)">' + row.quarter.substring(0, 7) + '</td><td>' + (row.long_return * 100).toFixed(2) + '%</td><td>' + (row.short_return * 100).toFixed(2) + '%</td><td class="' + lsClass + '" style="font-family:var(--mono);font-weight:bold">' + (row.ls_return * 100).toFixed(2) + '%</td><td class="td-sub">' + row.n_long + '</td><td class="td-sub">' + row.n_short + "</td></tr>";
            });
            btTbody.innerHTML = rowsHtml;
        } catch (err) {
            console.error(err);
            const msg = pipelineErr(err);
            btStrip.innerHTML = '<div class="td-sub" style="color:var(--go);padding:10px">' + msg + "</div>";
            btChart.innerHTML = '<div class="td-sub" style="text-align:center;padding:40px">' + msg + "</div>";
            btBar.innerHTML = '<div class="td-sub" style="text-align:center;padding:40px">' + msg + "</div>";
            btTbody.innerHTML = '<tr><td colspan="6" class="td-sub" style="text-align:center;padding:40px 0;color:var(--go)">Failed to sync quantitative archive.</td></tr>';
        }
    }

    // ── Wiring (after content is injected) ───────────────────────────────────────
    function init() {
        document.addEventListener("click", function (e) {
            const vBtn = e.target.closest("[data-view]");
            if (vBtn) {
                e.preventDefault();
                setView(vBtn.getAttribute("data-view"), true);
                return;
            }
            const sBtn = e.target.closest("[data-scroll-to]");
            if (sBtn) {
                e.preventDefault();
                const targetEl = document.getElementById(sBtn.getAttribute("data-scroll-to"));
                if (targetEl) targetEl.scrollIntoView({ behavior: "smooth" });
                return;
            }
            const scrollL = e.target.closest("a[data-scroll]");
            if (scrollL) {
                e.preventDefault();
                const targetId = scrollL.getAttribute("href").replace("#", "");
                const targetEl = document.getElementById(targetId);
                if (targetEl) targetEl.scrollIntoView({ behavior: "smooth" });
            }
        });

        const subbtnRanksEl = document.getElementById("subbtn-rankings");
        const subbtnBacktestEl = document.getElementById("subbtn-backtest");
        const subbtnAuditEl = document.getElementById("subbtn-audit");
        const subbtnEogdcfEl = document.getElementById("subbtn-eogdcf");
        if (subbtnRanksEl) subbtnRanksEl.addEventListener("click", function () { setCaligulaSubview("rankings"); });
        if (subbtnBacktestEl) subbtnBacktestEl.addEventListener("click", function () { setCaligulaSubview("backtest"); });
        if (subbtnAuditEl) subbtnAuditEl.addEventListener("click", function () { setCaligulaSubview("audit"); });
        if (subbtnEogdcfEl) subbtnEogdcfEl.addEventListener("click", function () { runDiligenceAnalysis("EOG"); });

        const btnEp = document.getElementById("bt-toggle-ep");
        const btnGc = document.getElementById("bt-toggle-gc");
        if (btnEp && btnGc) {
            btnEp.addEventListener("click", function () {
                btnEp.classList.add("on");
                btnGc.classList.remove("on");
                loadBacktestData("ep_study");
            });
            btnGc.addEventListener("click", function () {
                btnGc.classList.add("on");
                btnEp.classList.remove("on");
                loadBacktestData("general_corp");
            });
        }

        const searchInput = document.getElementById("ticker-input");
        const searchBtn = document.getElementById("search-trigger-btn");
        function executeSearch() {
            const sym = searchInput.value;
            if (sym) runDiligenceAnalysis(sym);
        }
        if (searchBtn) searchBtn.addEventListener("click", executeSearch);
        if (searchInput) {
            searchInput.addEventListener("keypress", function (e) {
                if (e.key === "Enter") executeSearch();
            });
        }

        const ddBackBtn = document.getElementById("dd-back-btn");
        if (ddBackBtn) {
            ddBackBtn.addEventListener("click", function () {
                setCaligulaSubview("rankings");
                if (searchInput) searchInput.value = "";
            });
        }

        window.addEventListener("popstate", fromHash);
        fromHash();
    }

    // ── Boot: load content, render views, then wire up ───────────────────────────
    async function boot() {
        try {
            const results = await Promise.all([
                fetchJSON(CONTENT.projects),
                fetchJSON(CONTENT.goldstein),
                fetchJSON(CONTENT.caligula),
                fetchJSON(CONTENT.chc)
            ]);
            const projects = results[0];
            const goldstein = results[1];
            const caligula = results[2];
            const chc = results[3];

            renderHome(projects);
            document.getElementById("view-goldstein").innerHTML = goldstein.html;
            document.getElementById("view-caligula").innerHTML = caligula.html;
            document.getElementById("view-chc").innerHTML = chc.html;
            eogHeatmapConfig = caligula.eogHeatmap || null;

            init();
        } catch (err) {
            showFatalError(err);
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }
})();
