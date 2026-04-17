/* Auto-redirect to the user's preferred locale on first visit.
 *
 * Order of preference:
 *   1. Explicit override in localStorage (set when the user clicks a link
 *      in the languages section).
 *   2. Best match against navigator.languages.
 *   3. Default English (no redirect).
 *
 * After a redirect we set sessionStorage['vultyr_redirected'] = '1' to avoid
 * loops, and we never auto-redirect away from a locale-prefixed URL — if the
 * user lands directly on /de/services.html we trust that.
 */
(function () {
    var SUPPORTED = [
        "en", "da", "de", "es", "fr", "it", "ja", "ko", "nb", "nl",
        "pt-BR", "ru", "sv", "tr", "vi", "zh-Hans", "zh-Hant"
    ];
    var DEFAULT = "en";
    var STORAGE_KEY = "vultyr_locale";
    var REDIRECT_FLAG = "vultyr_redirected";

    function safeGet(storage, key) {
        try { return storage.getItem(key); } catch (e) { return null; }
    }
    function safeSet(storage, key, value) {
        try { storage.setItem(key, value); } catch (e) { /* ignore quota / disabled */ }
    }

    function pathLocale(path) {
        var m = path.match(/^\/([a-z]{2}(?:-[A-Za-z]+)?)(?:\/|$)/);
        if (m && SUPPORTED.indexOf(m[1]) >= 0) return m[1];
        return DEFAULT;
    }

    function matchLocale(tag) {
        if (!tag) return null;
        if (SUPPORTED.indexOf(tag) >= 0) return tag;
        // Common Chinese mappings that won't match exactly.
        if (/^zh\b/i.test(tag)) {
            if (/Hans|CN|SG|MY/i.test(tag)) return "zh-Hans";
            if (/Hant|TW|HK|MO/i.test(tag)) return "zh-Hant";
            return "zh-Hans";
        }
        // Portuguese collapses to pt-BR (we don't ship pt-PT).
        if (/^pt\b/i.test(tag)) return "pt-BR";
        // Norwegian: bokmål, nynorsk, generic "no" all map to nb.
        if (/^(no|nb|nn)\b/i.test(tag)) return "nb";
        // Generic "xx-YY" — try the base.
        var base = tag.split("-")[0].toLowerCase();
        if (SUPPORTED.indexOf(base) >= 0) return base;
        return null;
    }

    function detectPreferred() {
        var stored = safeGet(window.localStorage, STORAGE_KEY);
        if (stored && SUPPORTED.indexOf(stored) >= 0) return stored;

        var langs = navigator.languages && navigator.languages.length
            ? navigator.languages
            : [navigator.language || DEFAULT];
        for (var i = 0; i < langs.length; i++) {
            var match = matchLocale(langs[i]);
            if (match) return match;
        }
        return DEFAULT;
    }

    var current = pathLocale(window.location.pathname);
    var preferred = detectPreferred();

    // Already in the right place — nothing to do.
    if (current === preferred) return;

    // Don't redirect if we already did this session (prevents loops if the
    // user manually navigates back to a non-preferred locale).
    if (safeGet(window.sessionStorage, REDIRECT_FLAG)) return;

    // Build the target URL: strip any current locale prefix, then add the
    // preferred prefix (or none for English).
    var path = window.location.pathname;
    if (current !== DEFAULT) {
        path = path.replace(new RegExp("^/" + current + "(/|$)"), "/");
    }
    var target = preferred === DEFAULT ? path : "/" + preferred + path;

    safeSet(window.sessionStorage, REDIRECT_FLAG, "1");
    window.location.replace(target + window.location.search + window.location.hash);
})();
