/* Persist the user's explicit locale choice so locale-detect.js stops
 * second-guessing them, and manage the topbar language dropdown
 * (outside-click and ESC close — <details> handles toggle natively). */
(function () {
    var STORAGE_KEY = "vultyr_locale";

    document.addEventListener("click", function (event) {
        var target = event.target;
        if (!target || !target.closest) return;

        var link = target.closest(
            ".languages-section a[data-locale], .lang-menu-panel a[data-locale]"
        );
        if (link) {
            try {
                window.localStorage.setItem(STORAGE_KEY, link.getAttribute("data-locale"));
            } catch (e) { /* ignore */ }
        }

        var openMenus = document.querySelectorAll(".lang-menu[open]");
        if (!openMenus.length) return;
        for (var i = 0; i < openMenus.length; i++) {
            if (!openMenus[i].contains(target)) openMenus[i].removeAttribute("open");
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key !== "Escape") return;
        var openMenus = document.querySelectorAll(".lang-menu[open]");
        for (var i = 0; i < openMenus.length; i++) {
            openMenus[i].removeAttribute("open");
            var summary = openMenus[i].querySelector("summary");
            if (summary) summary.focus();
        }
    });
})();
