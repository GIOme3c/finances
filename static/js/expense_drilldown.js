(function () {
    function ready(fn) {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", fn);
        } else {
            fn();
        }
    }

    ready(function () {
        document.querySelectorAll("[data-tree-drill]").forEach(function (root) {
            root.addEventListener("click", function (event) {
                const toggle = event.target.closest("[data-tree-toggle]");
                if (!toggle || !root.contains(toggle)) {
                    return;
                }

                const children = toggle.nextElementSibling;
                if (!children || !children.classList.contains("expense-drill-children")) {
                    return;
                }

                const willOpen = children.hidden;
                children.hidden = !willOpen;
                toggle.setAttribute("aria-expanded", willOpen ? "true" : "false");
                toggle.classList.toggle("is-open", willOpen);
            });
        });
    });
})();
