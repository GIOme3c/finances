(function () {
    function ready(fn) {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", fn);
        } else {
            fn();
        }
    }

    ready(function () {
        const form = document.getElementById("transferCreateForm");
        if (!form) {
            return;
        }

        let datePicker = null;

        function clearErrors() {
            const box = document.getElementById("transferCreateFormErrors");
            if (box) {
                box.hidden = true;
                box.innerHTML = "";
            }
            form.querySelectorAll("[data-field-error]").forEach((el) => {
                el.hidden = true;
                el.textContent = "";
            });
        }

        function showErrors(errors) {
            clearErrors();
            const box = document.getElementById("transferCreateFormErrors");
            const nonField = errors.__all__ || errors.non_field_errors;
            if (nonField && box) {
                box.hidden = false;
                nonField.forEach((msg) => {
                    const li = document.createElement("div");
                    li.textContent = msg;
                    box.appendChild(li);
                });
            }
            Object.keys(errors).forEach((field) => {
                if (field === "__all__" || field === "non_field_errors") {
                    return;
                }
                const el = form.querySelector(`[data-field-error="${field}"]`);
                if (el && errors[field] && errors[field][0]) {
                    el.hidden = false;
                    el.textContent = errors[field][0];
                }
            });
        }

        const transferModal = document.getElementById("transferCreateModal");
        if (transferModal) {
            transferModal.addEventListener("shown.bs.modal", function () {
                if (window.flatpickr && !datePicker) {
                    datePicker = flatpickr("#transfer_date", {
                        dateFormat: "d.m.Y",
                        locale: "ru",
                        allowInput: false,
                    });
                }
            });
            transferModal.addEventListener("hidden.bs.modal", function () {
                clearErrors();
            });
        }

        form.addEventListener("submit", function (event) {
            event.preventDefault();
            clearErrors();
            const submitBtn = document.getElementById("transferCreateSubmit");
            if (submitBtn) {
                submitBtn.disabled = true;
            }

            fetch(form.action, {
                method: "POST",
                body: new FormData(form),
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            })
                .then(async (response) => {
                    const data = await response.json();
                    if (response.ok && data.success) {
                        window.location.reload();
                        return;
                    }
                    if (data.errors) {
                        showErrors(data.errors);
                    } else {
                        showErrors({ __all__: [data.error || "Не удалось сохранить перевод"] });
                    }
                })
                .catch(() => {
                    showErrors({ __all__: ["Не удалось сохранить перевод"] });
                })
                .finally(() => {
                    if (submitBtn) {
                        submitBtn.disabled = false;
                    }
                });
        });
    });
})();
