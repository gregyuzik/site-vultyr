/* Persist the user's explicit locale choice so locale-detect.js stops
 * second-guessing them. Bound at document level so it survives any
 * future re-renders of the languages section. */
(function () {
    var STORAGE_KEY = "vultyr_locale";
    document.addEventListener("click", function (event) {
        var link = event.target.closest && event.target.closest(".languages-section a[data-locale]");
        if (!link) return;
        try {
            window.localStorage.setItem(STORAGE_KEY, link.getAttribute("data-locale"));
        } catch (e) { /* ignore */ }
    });
})();
