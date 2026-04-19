/* Persist the user's explicit locale choice (clicked from the bottom
 * languages section) so locale-detect.js stops second-guessing them. */
(function () {
    var STORAGE_KEY = "vultyr_locale";

    document.addEventListener("click", function (event) {
        var target = event.target;
        if (!target || !target.closest) return;

        var link = target.closest(".languages-section a[data-locale]");
        if (!link) return;
        try {
            window.localStorage.setItem(STORAGE_KEY, link.getAttribute("data-locale"));
        } catch (e) { /* ignore */ }
    });
})();
