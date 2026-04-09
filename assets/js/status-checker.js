/**
 * Vultyr Status Checker
 * Client-side status checking via Statuspage.io API with sessionStorage caching.
 */
(function () {
  "use strict";

  var CACHE_PREFIX = "vultyr_status_";
  var CACHE_TTL = 5 * 60 * 1000; // 5 minutes

  function getCached(slug) {
    try {
      var raw = sessionStorage.getItem(CACHE_PREFIX + slug);
      if (!raw) return null;
      var data = JSON.parse(raw);
      if (Date.now() - data.ts > CACHE_TTL) {
        sessionStorage.removeItem(CACHE_PREFIX + slug);
        return null;
      }
      return data;
    } catch (e) {
      return null;
    }
  }

  function setCache(slug, indicator, description) {
    try {
      sessionStorage.setItem(
        CACHE_PREFIX + slug,
        JSON.stringify({ indicator: indicator, description: description, ts: Date.now() })
      );
    } catch (e) {}
  }

  function checkStatus(apiUrl, slug) {
    var cached = getCached(slug);
    if (cached) return Promise.resolve(cached);

    // Use summary.json instead of status.json to catch active incidents
    var summaryUrl = apiUrl.replace(/\/status\.json$/, "/summary.json");

    var controller =
      typeof AbortController !== "undefined" ? new AbortController() : null;
    var timeoutId = controller
      ? setTimeout(function () { controller.abort(); }, 8000)
      : null;

    return fetch(summaryUrl, {
      signal: controller ? controller.signal : undefined,
    })
      .then(function (resp) {
        if (timeoutId) clearTimeout(timeoutId);
        if (!resp.ok) throw new Error("HTTP " + resp.status);
        return resp.json();
      })
      .then(function (json) {
        var indicator = json.status.indicator;
        var description = json.status.description;

        // Check for active incidents that the top-level status may not reflect
        var incidents = json.incidents || [];
        if (incidents.length > 0 && indicator === "none") {
          var latest = incidents[0];
          var impact = latest.impact || "minor";
          indicator = impact === "none" ? "minor" : impact;
          description = latest.name || "Active incident";
        }

        setCache(slug, indicator, description);
        return { indicator: indicator, description: description };
      })
      .catch(function () {
        if (timeoutId) clearTimeout(timeoutId);
        return { indicator: "unknown", description: "Unable to check" };
      });
  }

  function checkMultiple(services, onResult) {
    var delay = 0;
    services.forEach(function (svc) {
      setTimeout(function () {
        checkStatus(svc.apiUrl, svc.slug).then(function (result) {
          if (onResult) onResult(svc.slug, result);
        });
      }, delay);
      delay += 100; // stagger requests by 100ms
    });
  }

  var COLORS = {
    none: "#00ff41",
    minor: "#ff9926",
    major: "#ff4444",
    critical: "#ff0000",
    unknown: "#555",
  };

  var LABELS = {
    none: "Operational",
    minor: "Minor Issues",
    major: "Major Outage",
    critical: "Critical Outage",
    unknown: "Unknown",
  };

  window.VultyrStatus = {
    checkStatus: checkStatus,
    checkMultiple: checkMultiple,
    COLORS: COLORS,
    LABELS: LABELS,
  };
})();
