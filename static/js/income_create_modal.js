(function () {
    function ready(fn) {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", fn);
        } else {
            fn();
        }
    }

    ready(function () {
        const form = document.getElementById("incomeCreateForm");
        if (!form) {
            return;
        }

        const scriptTag = document.querySelector("script[data-income-category-url]");
        const categoryUrl = scriptTag && scriptTag.dataset.incomeCategoryUrl;
        const categorySelect = document.getElementById("income_category");
        let datePicker = null;

        function clearErrors() {
            const box = document.getElementById("incomeCreateFormErrors");
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
            const box = document.getElementById("incomeCreateFormErrors");
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

        const incomeModal = document.getElementById("incomeCreateModal");
        if (incomeModal) {
            incomeModal.addEventListener("shown.bs.modal", function () {
                if (window.flatpickr && !datePicker) {
                    datePicker = flatpickr("#income_date", {
                        dateFormat: "d.m.Y",
                        locale: "ru",
                        allowInput: false,
                    });
                }
            });
            incomeModal.addEventListener("hidden.bs.modal", function () {
                clearErrors();
            });
        }

        form.addEventListener("submit", function (event) {
            event.preventDefault();
            clearErrors();
            const submitBtn = document.getElementById("incomeCreateSubmit");
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
                        showErrors({ __all__: [data.error || "Не удалось сохранить доход"] });
                    }
                })
                .catch(() => {
                    showErrors({ __all__: ["Не удалось сохранить доход"] });
                })
                .finally(() => {
                    if (submitBtn) {
                        submitBtn.disabled = false;
                    }
                });
        });

        const addCategoryBtn = document.getElementById("addIncomeCategoryBtn");
        if (addCategoryBtn) {
            addCategoryBtn.addEventListener("click", function () {
                const catForm = document.getElementById("addIncomeCategoryForm");
                const formData = new FormData(catForm);
                fetch(categoryUrl, {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
                        "X-Requested-With": "XMLHttpRequest",
                    },
                })
                    .then((response) => response.json())
                    .then((data) => {
                        if (!data.success) {
                            alert(data.error || "Ошибка при добавлении категории");
                            return;
                        }
                        categorySelect.add(new Option(data.name, data.id, true, true));
                        bootstrap.Modal.getInstance(
                            document.getElementById("addIncomeCategoryModal")
                        ).hide();
                        catForm.reset();
                    });
            });
        }
    });
})();
