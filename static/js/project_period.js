(function () {
    function ready(fn) {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", fn);
        } else {
            fn();
        }
    }

    ready(function () {
        const form = document.querySelector("[data-period-form]");
        if (!form) {
            return;
        }

        form.querySelectorAll("[data-period-auto-submit]").forEach((input) => {
            input.addEventListener("change", function () {
                form.submit();
            });
        });

        if (window.flatpickr) {
            form.querySelectorAll("[data-datepicker]").forEach((input) => {
                flatpickr(input, {
                    dateFormat: "d.m.Y",
                    locale: "ru",
                    allowInput: false,
                });
            });
        }
    });
})();
