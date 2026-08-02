from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Sum
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from calendar import monthrange
from datetime import date, datetime, timedelta
from decimal import Decimal
from urllib.parse import urlencode

from user_profile.models import Project
from accaunting import models as acc_models
from accaunting.views import (
    _expense_modal_context,
    _income_modal_context,
    _transfer_modal_context,
    _wallet_modal_context,
)


PERIOD_CHOICES = (
    ("current_month", "Текущий месяц"),
    ("month", "Месяц"),
    ("week", "Неделя"),
    ("today", "Сегодня"),
    ("custom", "Произвольный"),
)

_MONTHS_RU = (
    "",
    "январь",
    "февраль",
    "март",
    "апрель",
    "май",
    "июнь",
    "июль",
    "август",
    "сентябрь",
    "октябрь",
    "ноябрь",
    "декабрь",
)


def _parse_query_date(value):
    if not value:
        return None
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except (TypeError, ValueError):
            continue
    return None


def _month_bounds(year, month):
    last_day = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def _format_period_label(period, date_from, date_to):
    if date_from == date_to:
        return date_from.strftime("%d.%m.%Y")
    if period in ("current_month", "month"):
        month_end = _month_bounds(date_from.year, date_from.month)[1]
        if date_from.day == 1 and date_to == month_end:
            return f"{_MONTHS_RU[date_from.month]} {date_from.year}"
    return f"{date_from.strftime('%d.%m.%Y')}–{date_to.strftime('%d.%m.%Y')}"


def resolve_project_period(query_dict):
    today = timezone.localdate()
    raw_period = (query_dict.get("period") or "current_month").strip()
    valid = {key for key, _ in PERIOD_CHOICES}
    period = raw_period if raw_period in valid else "current_month"

    month_value = (query_dict.get("month") or "").strip()
    if not month_value:
        month_value = today.strftime("%Y-%m")

    date_from = _parse_query_date(query_dict.get("from"))
    date_to = _parse_query_date(query_dict.get("to"))

    if period == "current_month":
        date_from, date_to = _month_bounds(today.year, today.month)
        month_value = today.strftime("%Y-%m")
    elif period == "month":
        try:
            year_s, month_s = month_value.split("-", 1)
            year, month = int(year_s), int(month_s)
            if month < 1 or month > 12:
                raise ValueError
            date_from, date_to = _month_bounds(year, month)
            month_value = f"{year:04d}-{month:02d}"
        except (TypeError, ValueError):
            date_from, date_to = _month_bounds(today.year, today.month)
            month_value = today.strftime("%Y-%m")
    elif period == "week":
        date_from = today - timedelta(days=today.weekday())
        date_to = date_from + timedelta(days=6)
    elif period == "today":
        date_from = date_to = today
    else:  # custom
        if date_from is None:
            date_from = date(today.year, today.month, 1)
        if date_to is None:
            date_to = today
        if date_from > date_to:
            date_from, date_to = date_to, date_from

    options = []
    for key, title in PERIOD_CHOICES:
        params = {"period": key}
        if key == "month":
            params["month"] = month_value
        elif key == "custom":
            params["from"] = date_from.strftime("%d.%m.%Y")
            params["to"] = date_to.strftime("%d.%m.%Y")
        options.append({
            "key": key,
            "title": title,
            "active": key == period,
            "query": urlencode(params),
        })

    return {
        "period": period,
        "date_from": date_from,
        "date_to": date_to,
        "label": _format_period_label(period, date_from, date_to),
        "month_value": month_value,
        "from_value": date_from.strftime("%d.%m.%Y"),
        "to_value": date_to.strftime("%d.%m.%Y"),
        "options": options,
    }



def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический вход после регистрации
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')  # Замените 'home' на имя вашего URL
        else:
            messages.error(request, 'Ошибка регистрации. Проверьте данные.')
    else:
        form = UserCreationForm()

    return render(request, 'profile/register.html', {'form': form})


def user_profile(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        return render(request, 'profile/profile.html', {
            "projects": profile.all_projects,
        })
    return redirect('login')


class ProjectCreateView(CreateView):
    model = Project
    fields = ["name", "members"]
    template_name = "profile/project_update.html"
    success_url = reverse_lazy('profile')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['members'].queryset = form.fields['members'].queryset.exclude(id=self.request.user.profile.id)
        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user.profile
        return super().form_valid(form)


class ProjectUpdateView(UpdateView):
    model = Project
    fields = ["name", "members", "is_active"]
    template_name = "profile/project_update.html"
    success_url = reverse_lazy('profile')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['members'].queryset = form.fields['members'].queryset.exclude(id=self.request.user.profile.id)
        return form
    

class ProjectDeleteView(DeleteView):
    model = Project
    template_name = "profile/project_delete.html"
    success_url = reverse_lazy('profile')


class ProjectDetailView(DetailView):
    model = Project
    template_name = "profile/project_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        period = resolve_project_period(self.request.GET)
        date_from = period["date_from"]
        date_to = period["date_to"]

        expenses_qs = acc_models.ExpensesHistory.objects.filter(project=project)
        recent_expenses_qs = expenses_qs.filter(date__gte=date_from, date__lte=date_to)
        income_qs = acc_models.IncomeHistory.objects.filter(project=project)
        recent_income_qs = income_qs.filter(date__gte=date_from, date__lte=date_to)
        transfers_qs = acc_models.TransactionsHistory.objects.filter(project=project)
        recent_transfers_qs = transfers_qs.filter(date__gte=date_from, date__lte=date_to)
        wallets = acc_models.Wallet.objects.filter(project=project, is_active=True).order_by("name")

        context["wallets"] = wallets
        context["expenses_total"] = expenses_qs.aggregate(total=Sum("value"))["total"] or 0
        context["income_total"] = income_qs.aggregate(total=Sum("value"))["total"] or 0
        context["balance_total"] = sum((w.current_value for w in wallets), 0)
        context["members"] = project.members.all()
        context["period"] = period
        context["expense_categories"] = self._build_expense_categories(project, recent_expenses_qs)
        context["income_categories"] = self._build_income_categories(project, recent_income_qs)
        context["recent_transfers"] = self._build_recent_transfers(project, recent_transfers_qs)
        context.update(_expense_modal_context(project))
        context.update(_income_modal_context(project))
        context.update(_wallet_modal_context(project))
        context.update(_transfer_modal_context(project))
        return context

    def _build_expense_categories(self, project, expenses_qs):
        expenses = list(
            expenses_qs.select_related("category", "subcategory", "wallet")
            .order_by("-date", "-id")
        )
        if not expenses:
            return []

        categories = {}
        for expense in expenses:
            category = expense.category
            subcategory = expense.subcategory
            cat_bucket = categories.setdefault(
                category.id,
                {
                    "id": category.id,
                    "name": category.name,
                    "total": Decimal("0"),
                    "subcategories": {},
                },
            )
            cat_bucket["total"] += expense.value

            sub_bucket = cat_bucket["subcategories"].setdefault(
                subcategory.id,
                {
                    "id": subcategory.id,
                    "name": subcategory.name,
                    "total": Decimal("0"),
                    "expenses": [],
                },
            )
            sub_bucket["total"] += expense.value
            sub_bucket["expenses"].append({
                "id": expense.id,
                "date": expense.date,
                "value": expense.value,
                "wallet": str(expense.wallet),
                "comment": expense.comment or "",
                "update_url": reverse(
                    "expenses-update",
                    kwargs={"pr_pk": project.pk, "pk": expense.pk},
                ),
                "delete_url": reverse(
                    "expenses-delete",
                    kwargs={"pr_pk": project.pk, "pk": expense.pk},
                ),
            })

        result = []
        for cat in sorted(categories.values(), key=lambda item: item["total"], reverse=True):
            subs = sorted(
                cat["subcategories"].values(),
                key=lambda item: item["total"],
                reverse=True,
            )
            for sub in subs:
                sub["expenses"] = sorted(
                    sub["expenses"],
                    key=lambda item: (item["date"], item["id"]),
                )
            result.append({
                "id": cat["id"],
                "name": cat["name"],
                "total": cat["total"],
                "subcategories": subs,
            })
        return result

    def _build_income_categories(self, project, income_qs):
        incomes = list(
            income_qs.select_related("category", "wallet").order_by("-date", "-id")
        )
        if not incomes:
            return []

        categories = {}
        for income in incomes:
            category = income.category
            cat_bucket = categories.setdefault(
                category.id,
                {
                    "id": category.id,
                    "name": category.name,
                    "total": Decimal("0"),
                    "incomes": [],
                },
            )
            cat_bucket["total"] += income.value
            cat_bucket["incomes"].append({
                "id": income.id,
                "date": income.date,
                "value": income.value,
                "wallet": str(income.wallet),
                "comment": income.comment or "",
                "update_url": reverse(
                    "income-update",
                    kwargs={"pr_pk": project.pk, "pk": income.pk},
                ),
                "delete_url": reverse(
                    "income-delete",
                    kwargs={"pr_pk": project.pk, "pk": income.pk},
                ),
            })

        result = []
        for cat in sorted(categories.values(), key=lambda item: item["total"], reverse=True):
            cat["incomes"] = sorted(
                cat["incomes"],
                key=lambda item: (item["date"], item["id"]),
            )
            result.append(cat)
        return result

    def _build_recent_transfers(self, project, transfers_qs):
        transfers = list(
            transfers_qs.select_related("source", "aim").order_by("-date", "-id")
        )
        return [
            {
                "id": item.id,
                "date": item.date,
                "value": item.value,
                "source": str(item.source),
                "aim": str(item.aim),
                "comment": item.comment or "",
                "update_url": reverse(
                    "transfers-update",
                    kwargs={"pr_pk": project.pk, "pk": item.pk},
                ),
                "delete_url": reverse(
                    "transfers-delete",
                    kwargs={"pr_pk": project.pk, "pk": item.pk},
                ),
            }
            for item in transfers
        ]

