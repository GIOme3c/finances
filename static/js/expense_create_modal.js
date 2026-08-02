(function () {
    function ready(fn) {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", fn);
        } else {
            fn();
        }
    }

    ready(function () {
        const form = document.getElementById("expenseCreateForm");
        if (!form) {
            return;
        }

        const scriptTag = document.querySelector("script[data-category-url]");
        const categoryUrl = scriptTag && scriptTag.dataset.categoryUrl;
        const subcategoryUrl = scriptTag && scriptTag.dataset.subcategoryUrl;

        const categorySelect = document.getElementById("expense_category");
        const subcategorySelect = document.getElementById("expense_subcategory");
        const emptyLabel = "---------";
        const dataEl = document.getElementById("expense-subcategories-data");
        let subcategories = dataEl ? JSON.parse(dataEl.textContent) : [];

        let datePicker = null;

        function renderSubcategories(categoryId, selectedId) {
            if (!subcategorySelect) {
                return;
            }
            const selected = selectedId != null ? String(selectedId) : "";
            subcategorySelect.innerHTML = "";
            subcategorySelect.add(new Option(emptyLabel, ""));
            subcategories
                .filter((item) => !categoryId || String(item.category_id) === String(categoryId))
                .forEach((item) => {
                    subcategorySelect.add(
                        new Option(item.name, item.id, false, String(item.id) === selected)
                    );
                });
        }

        function clearErrors() {
            const box = document.getElementById("expenseCreateFormErrors");
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
            const box = document.getElementById("expenseCreateFormErrors");
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

        if (categorySelect) {
            categorySelect.addEventListener("change", function () {
                const categoryId = categorySelect.value;
                const currentSubId = subcategorySelect.value;
                const currentSub = subcategories.find(
                    (item) => String(item.id) === String(currentSubId)
                );
                const keepSelected =
                    categoryId &&
                    currentSub &&
                    String(currentSub.category_id) === String(categoryId)
                        ? currentSubId
                        : "";
                renderSubcategories(categoryId, keepSelected);
            });
        }

        if (subcategorySelect) {
            subcategorySelect.addEventListener("change", function () {
                if (categorySelect.value || !subcategorySelect.value) {
                    return;
                }
                const selected = subcategories.find(
                    (item) => String(item.id) === String(subcategorySelect.value)
                );
                if (!selected) {
                    return;
                }
                categorySelect.value = String(selected.category_id);
                renderSubcategories(selected.category_id, selected.id);
            });
        }

        renderSubcategories(
            categorySelect ? categorySelect.value : "",
            subcategorySelect ? subcategorySelect.value : ""
        );

        const expenseModal = document.getElementById("expenseCreateModal");
        if (expenseModal) {
            expenseModal.addEventListener("shown.bs.modal", function () {
                if (window.flatpickr && !datePicker) {
                    datePicker = flatpickr("#expense_date", {
                        dateFormat: "d.m.Y",
                        locale: "ru",
                        allowInput: false,
                    });
                }
            });
            expenseModal.addEventListener("hidden.bs.modal", function () {
                clearErrors();
            });
        }

        form.addEventListener("submit", function (event) {
            event.preventDefault();
            clearErrors();
            const submitBtn = document.getElementById("expenseCreateSubmit");
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
                        showErrors({ __all__: [data.error || "Не удалось сохранить расход"] });
                    }
                })
                .catch(() => {
                    showErrors({ __all__: ["Не удалось сохранить расход"] });
                })
                .finally(() => {
                    if (submitBtn) {
                        submitBtn.disabled = false;
                    }
                });
        });

        const addCategoryBtn = document.getElementById("addExpenseCategoryBtn");
        if (addCategoryBtn) {
            addCategoryBtn.addEventListener("click", function () {
                const catForm = document.getElementById("addExpenseCategoryForm");
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
                        document
                            .getElementById("expense_category_select_modal")
                            .add(new Option(data.name, data.id));
                        renderSubcategories(data.id, "");
                        bootstrap.Modal.getInstance(
                            document.getElementById("addExpenseCategoryModal")
                        ).hide();
                        catForm.reset();
                    });
            });
        }

        const addSubcategoryBtn = document.getElementById("addExpenseSubcategoryBtn");
        if (addSubcategoryBtn) {
            addSubcategoryBtn.addEventListener("click", function () {
                const subForm = document.getElementById("addExpenseSubcategoryForm");
                const formData = new FormData(subForm);
                fetch(subcategoryUrl, {
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
                            alert(data.error || "Ошибка при добавлении подкатегории");
                            return;
                        }
                        subcategories.push({
                            id: data.id,
                            name: data.name,
                            category_id: data.category_id,
                        });
                        categorySelect.value = String(data.category_id);
                        renderSubcategories(categorySelect.value, data.id);
                        bootstrap.Modal.getInstance(
                            document.getElementById("addExpenseSubcategoryModal")
                        ).hide();
                        subForm.reset();
                    });
            });
        }
    });
})();
