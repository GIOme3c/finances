from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views import View
from django.forms import DateInput, TextInput
from django.urls import reverse

from accaunting.forms import (
    ExpensesCategoryModelForm,
    ExpensesHistoryForm,
    ExpensesSubCategoryModelForm,
    IncomeCategoryModelForm,
    IncomeHistoryForm,
    TransactionsHistoryForm,
    WalletForm,
)
from accaunting.models import (
    ExpensesHistory,
    ExpensesSubCategory,
    IncomeHistory,
    TransactionsHistory,
    Wallet,
)

from user_profile import models as up_models


def _project_or_404(pr_pk):
    return get_object_or_404(up_models.Project, pk=pr_pk)


def _is_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _configure_history_form(form):
    form.fields["date"].widget = DateInput(
        attrs={
            "type": "text",
            "data-datepicker": "",
            "placeholder": "дд.мм.гггг",
        }
    )
    form.fields["comment"].widget = TextInput(
        attrs={"placeholder": "Комментарий"}
    )
    return form


def _subcategories_payload(project_id):
    return list(
        ExpensesSubCategory.objects.filter(project_id=project_id)
        .order_by("name")
        .values("id", "name", "category_id")
    )


def _expense_create_form(project):
    form = ExpensesHistoryForm(
        project=project,
        instance=ExpensesHistory(project_id=project.id),
        auto_id="expense_%s",
    )
    return _configure_history_form(form)


def _expense_modal_context(project):
    return {
        "pr_pk": project.id,
        "expense_form": _expense_create_form(project),
        "subcategories_data": _subcategories_payload(project.id),
    }


def _income_create_form(project):
    form = IncomeHistoryForm(
        project=project,
        instance=IncomeHistory(project_id=project.id),
        auto_id="income_%s",
    )
    return _configure_history_form(form)


def _income_modal_context(project):
    return {
        "pr_pk": project.id,
        "income_form": _income_create_form(project),
    }


def _wallet_create_form(project):
    return WalletForm(
        project=project,
        instance=Wallet(project_id=project.id),
        auto_id="wallet_%s",
    )


def _wallet_modal_context(project):
    return {
        "pr_pk": project.id,
        "wallet_form": _wallet_create_form(project),
    }


def _transfer_create_form(project):
    form = TransactionsHistoryForm(
        project=project,
        instance=TransactionsHistory(project_id=project.id),
        auto_id="transfer_%s",
    )
    return _configure_history_form(form)


def _transfer_modal_context(project):
    return {
        "pr_pk": project.id,
        "transfer_form": _transfer_create_form(project),
    }


def _apply_transfer_balances(source, aim, value, reverse=False):
    delta = -value if reverse else value
    source.current_value -= delta
    aim.current_value += delta
    source.save(update_fields=["current_value"])
    aim.save(update_fields=["current_value"])


class ExpensesHistoryRecordCreateView(CreateView):
    model = ExpensesHistory
    form_class = ExpensesHistoryForm
    template_name = "accaunting/expenses_history_record_update.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["project"] = _project_or_404(self.kwargs["pr_pk"])
        kwargs["instance"] = ExpensesHistory(project_id=self.kwargs["pr_pk"])
        return kwargs

    def get_form(self, form_class=None):
        return _configure_history_form(super().get_form(form_class))

    def get_success_url(self):
        return reverse("expenses-list", kwargs={"pr_pk": self.kwargs["pr_pk"]})

    def form_valid(self, form):
        if _is_ajax(self.request):
            self.object = form.save()
            return JsonResponse({
                "success": True,
                "redirect_url": self.get_success_url(),
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        if _is_ajax(self.request):
            return JsonResponse({
                "success": False,
                "errors": form.errors,
            }, status=400)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = _project_or_404(self.kwargs["pr_pk"])
        context["pr_pk"] = self.kwargs["pr_pk"]
        context["project"] = project
        context["subcategories_data"] = _subcategories_payload(project.id)
        return context


class ExpensesHistoryRecordUpdateView(UpdateView):
    model = ExpensesHistory
    form_class = ExpensesHistoryForm
    template_name = "accaunting/expenses_history_record_update.html"

    def get_queryset(self):
        return super().get_queryset().filter(project_id=self.kwargs["pr_pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["project"] = _project_or_404(self.kwargs["pr_pk"])
        return kwargs

    def get_form(self, form_class=None):
        return _configure_history_form(super().get_form(form_class))

    def get_success_url(self):
        return reverse("expenses-list", kwargs={"pr_pk": self.kwargs["pr_pk"]})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = _project_or_404(self.kwargs["pr_pk"])
        context["pr_pk"] = self.kwargs["pr_pk"]
        context["project"] = project
        context["subcategories_data"] = _subcategories_payload(project.id)
        return context


class ExpensesHistoryListView(ListView):
    model = ExpensesHistory
    template_name = "accaunting/expenses_history_list.html"
    paginate_by = 15

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(project__id=self.kwargs["pr_pk"])
            .select_related("category", "subcategory", "wallet")
            .order_by("-date", "-id")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pr_pk"] = self.kwargs["pr_pk"]
        context["project"] = _project_or_404(self.kwargs["pr_pk"])
        context.update(_expense_modal_context(context["project"]))
        return context


class ExpensesHistoryRecordDeleteView(DeleteView):
    model = ExpensesHistory
    template_name = "accaunting/expenses_history_record_delete.html"

    def get_queryset(self):
        return super().get_queryset().filter(project_id=self.kwargs["pr_pk"])

    def get_success_url(self):
        return reverse("expenses-list", kwargs={"pr_pk": self.object.project_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pr_pk"] = self.object.project_id
        context["project"] = self.object.project
        return context


class ExpensesCategoryCreateView(View):
    def post(self, request, pr_pk):
        form_data = request.POST.dict()
        form_data["project"] = pr_pk
        form = ExpensesCategoryModelForm(form_data)
        if form.is_valid():
            category = form.save()
            return JsonResponse({
                "success": True,
                "id": category.id,
                "name": category.name,
            })
        return JsonResponse({
            "success": False,
            "error": next(iter(form.errors.values()))[0],
        }, status=400)


class ExpensesSubCategoryCreateView(View):
    def post(self, request, pr_pk):
        form_data = request.POST.dict()
        form_data["project"] = pr_pk
        form = ExpensesSubCategoryModelForm(form_data)
        if form.is_valid():
            subcategory = form.save()
            return JsonResponse({
                "success": True,
                "id": subcategory.id,
                "name": subcategory.name,
                "category_id": subcategory.category_id,
            })
        return JsonResponse({
            "success": False,
            "error": next(iter(form.errors.values()))[0],
        }, status=400)


class IncomeHistoryRecordCreateView(CreateView):
    model = IncomeHistory
    form_class = IncomeHistoryForm
    template_name = "accaunting/income_history_record_update.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["project"] = _project_or_404(self.kwargs["pr_pk"])
        kwargs["instance"] = IncomeHistory(project_id=self.kwargs["pr_pk"])
        return kwargs

    def get_form(self, form_class=None):
        return _configure_history_form(super().get_form(form_class))

    def get_success_url(self):
        return reverse("income-list", kwargs={"pr_pk": self.kwargs["pr_pk"]})

    def form_valid(self, form):
        if _is_ajax(self.request):
            self.object = form.save()
            return JsonResponse({
                "success": True,
                "redirect_url": self.get_success_url(),
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        if _is_ajax(self.request):
            return JsonResponse({
                "success": False,
                "errors": form.errors,
            }, status=400)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pr_pk"] = self.kwargs["pr_pk"]
        context["project"] = _project_or_404(self.kwargs["pr_pk"])
        return context


class IncomeHistoryRecordUpdateView(UpdateView):
    model = IncomeHistory
    form_class = IncomeHistoryForm
    template_name = "accaunting/income_history_record_update.html"

    def get_queryset(self):
        return super().get_queryset().filter(project_id=self.kwargs["pr_pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["project"] = _project_or_404(self.kwargs["pr_pk"])
        return kwargs

    def get_form(self, form_class=None):
        return _configure_history_form(super().get_form(form_class))

    def get_success_url(self):
        return reverse("income-list", kwargs={"pr_pk": self.kwargs["pr_pk"]})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pr_pk"] = self.kwargs["pr_pk"]
        context["project"] = _project_or_404(self.kwargs["pr_pk"])
        return context


class IncomeHistoryListView(ListView):
    model = IncomeHistory
    template_name = "accaunting/income_history_list.html"
    paginate_by = 15

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(project__id=self.kwargs["pr_pk"])
            .select_related("category", "wallet")
            .order_by("-date", "-id")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pr_pk"] = self.kwargs["pr_pk"]
        context["project"] = _project_or_404(self.kwargs["pr_pk"])
        context.update(_income_modal_context(context["project"]))
        return context


class IncomeHistoryRecordDeleteView(DeleteView):
    model = IncomeHistory
    template_name = "accaunting/income_history_record_delete.html"

    def get_queryset(self):
        return super().get_queryset().filter(project_id=self.kwargs["pr_pk"])

    def get_success_url(self):
        return reverse("income-list", kwargs={"pr_pk": self.object.project_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pr_pk"] = self.object.project_id
        context["project"] = self.object.project
        return context


class IncomeCategoryCreateView(View):
    def post(self, request, pr_pk):
        form_data = request.POST.dict()
        form_data["project"] = pr_pk
        form = IncomeCategoryModelForm(form_data)
        if form.is_valid():
            category = form.save()
            return JsonResponse({
                "success": True,
                "id": category.id,
                "name": category.name,
            })
        return JsonResponse({
            "success": False,
            "error": next(iter(form.errors.values()))[0],
        }, status=400)


class WalletCreateView(CreateView):
    model = Wallet
    form_class = WalletForm

    def get(self, request, *args, **kwargs):
        return redirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["project"] = _project_or_404(self.kwargs["pr_pk"])
        kwargs["instance"] = Wallet(project_id=self.kwargs["pr_pk"])
        return kwargs

    def get_success_url(self):
        return reverse("project-detail", kwargs={"pk": self.kwargs["pr_pk"]})

    def form_valid(self, form):
        if _is_ajax(self.request):
            self.object = form.save()
            return JsonResponse({
                "success": True,
                "redirect_url": self.get_success_url(),
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        if _is_ajax(self.request):
            return JsonResponse({
                "success": False,
                "errors": form.errors,
            }, status=400)
        return redirect(self.get_success_url())


class TransactionsHistoryListView(ListView):
    model = TransactionsHistory
    template_name = "accaunting/transactions_history_list.html"
    paginate_by = 15

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(project__id=self.kwargs["pr_pk"])
            .select_related("source", "aim")
            .order_by("-date", "-id")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pr_pk"] = self.kwargs["pr_pk"]
        context["project"] = _project_or_404(self.kwargs["pr_pk"])
        context.update(_transfer_modal_context(context["project"]))
        return context


class TransactionsHistoryRecordCreateView(CreateView):
    model = TransactionsHistory
    form_class = TransactionsHistoryForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["project"] = _project_or_404(self.kwargs["pr_pk"])
        kwargs["instance"] = TransactionsHistory(project_id=self.kwargs["pr_pk"])
        return kwargs

    def get_form(self, form_class=None):
        return _configure_history_form(super().get_form(form_class))

    def get_success_url(self):
        return reverse("transfers-list", kwargs={"pr_pk": self.kwargs["pr_pk"]})

    @transaction.atomic
    def form_valid(self, form):
        self.object = form.save()
        source = Wallet.objects.select_for_update().get(pk=self.object.source_id)
        aim = Wallet.objects.select_for_update().get(pk=self.object.aim_id)
        _apply_transfer_balances(source, aim, self.object.value)
        if _is_ajax(self.request):
            return JsonResponse({
                "success": True,
                "redirect_url": self.get_success_url(),
            })
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        if _is_ajax(self.request):
            return JsonResponse({
                "success": False,
                "errors": form.errors,
            }, status=400)
        return redirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        return redirect(self.get_success_url())


class TransactionsHistoryRecordUpdateView(UpdateView):
    model = TransactionsHistory
    form_class = TransactionsHistoryForm
    template_name = "accaunting/transactions_history_record_update.html"

    def get_queryset(self):
        return super().get_queryset().filter(project_id=self.kwargs["pr_pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["project"] = _project_or_404(self.kwargs["pr_pk"])
        return kwargs

    def get_form(self, form_class=None):
        return _configure_history_form(super().get_form(form_class))

    def get_success_url(self):
        return reverse("transfers-list", kwargs={"pr_pk": self.kwargs["pr_pk"]})

    @transaction.atomic
    def form_valid(self, form):
        old = TransactionsHistory.objects.select_related("source", "aim").get(pk=self.object.pk)
        old_source = Wallet.objects.select_for_update().get(pk=old.source_id)
        old_aim = Wallet.objects.select_for_update().get(pk=old.aim_id)
        _apply_transfer_balances(old_source, old_aim, old.value, reverse=True)

        self.object = form.save()
        source = Wallet.objects.select_for_update().get(pk=self.object.source_id)
        aim = Wallet.objects.select_for_update().get(pk=self.object.aim_id)
        _apply_transfer_balances(source, aim, self.object.value)
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pr_pk"] = self.kwargs["pr_pk"]
        context["project"] = _project_or_404(self.kwargs["pr_pk"])
        return context


class TransactionsHistoryRecordDeleteView(DeleteView):
    model = TransactionsHistory
    template_name = "accaunting/transactions_history_record_delete.html"

    def get_queryset(self):
        return super().get_queryset().filter(project_id=self.kwargs["pr_pk"])

    def get_success_url(self):
        return reverse("transfers-list", kwargs={"pr_pk": self.object.project_id})

    @transaction.atomic
    def form_valid(self, form):
        self.object = self.get_object()
        source = Wallet.objects.select_for_update().get(pk=self.object.source_id)
        aim = Wallet.objects.select_for_update().get(pk=self.object.aim_id)
        _apply_transfer_balances(source, aim, self.object.value, reverse=True)
        success_url = self.get_success_url()
        self.object.delete()
        return redirect(success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pr_pk"] = self.object.project_id
        context["project"] = self.object.project
        return context
