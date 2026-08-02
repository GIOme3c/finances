from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accaunting.models import (
    Credit,
    CreditHistory,
    ExpensesCategory,
    ExpensesHistory,
    ExpensesSubCategory,
    IncomeCategory,
    IncomeHistory,
    Planes,
    TransactionsHistory,
    Wallet,
)
from user_profile.models import Project


def _clear_project_accounting(project):
    CreditHistory.objects.filter(project=project).delete()
    Credit.objects.filter(project=project).delete()
    Planes.objects.filter(project=project).delete()
    TransactionsHistory.objects.filter(project=project).delete()
    ExpensesHistory.objects.filter(project=project).delete()
    IncomeHistory.objects.filter(project=project).delete()
    ExpensesSubCategory.objects.filter(project=project).delete()
    ExpensesCategory.objects.filter(project=project).delete()
    IncomeCategory.objects.filter(project=project).delete()
    Wallet.objects.filter(project=project).delete()


def _seed_project(project, rich=True):
    cash = Wallet.objects.create(
        project=project,
        name="Наличные",
        current_value=Decimal("12500.00"),
    )
    card = Wallet.objects.create(
        project=project,
        name="Карта",
        current_value=Decimal("84320.50"),
    )
    savings = Wallet.objects.create(
        project=project,
        name="Накопления",
        current_value=Decimal("150000.00"),
        is_keeping=True,
    )

    income_defs = ["Зарплата", "Фриланс", "Подарки"]
    if not rich:
        income_defs = ["Зарплата", "Прочее"]
    income_cats = {
        name: IncomeCategory.objects.create(project=project, name=name)
        for name in income_defs
    }

    expense_tree = {
        "Еда": ["Продукты", "Кафе", "Доставка"],
        "Транспорт": ["Такси", "Метро", "Бензин"],
        "Жильё": ["Аренда", "Коммуналка", "Интернет"],
        "Развлечения": ["Кино", "Подписки"],
    }
    if not rich:
        expense_tree = {
            "Еда": ["Продукты", "Кафе"],
            "Транспорт": ["Такси", "Метро"],
            "Прочее": ["Разное"],
        }

    expense_cats = {}
    expense_subs = {}
    for cat_name, sub_names in expense_tree.items():
        cat = ExpensesCategory.objects.create(project=project, name=cat_name)
        expense_cats[cat_name] = cat
        expense_subs[cat_name] = {}
        for sub_name in sub_names:
            expense_subs[cat_name][sub_name] = ExpensesSubCategory.objects.create(
                project=project,
                category=cat,
                name=sub_name,
            )

    today = timezone.localdate()

    incomes = [
        (today.replace(day=5) if today.day >= 5 else today - timedelta(days=20), "Зарплата", "95000.00", card, "Основная работа"),
        (today - timedelta(days=12), "Фриланс", "18000.00", card, "Макет лендинга"),
        (today - timedelta(days=3), "Подарки", "5000.00", cash, "День рождения"),
    ]
    if not rich:
        incomes = [
            (today - timedelta(days=7), "Зарплата", "60000.00", card, None),
            (today - timedelta(days=2), "Прочее", "3000.00", cash, "Возврат долга"),
        ]

    for day, cat_name, value, wallet, comment in incomes:
        if cat_name not in income_cats:
            continue
        IncomeHistory.objects.create(
            project=project,
            date=day,
            value=Decimal(value),
            category=income_cats[cat_name],
            wallet=wallet,
            comment=comment or "",
        )

    expenses = [
        (today - timedelta(days=1), "Еда", "Продукты", "2450.00", card, "Пятёрочка"),
        (today - timedelta(days=2), "Еда", "Кафе", "890.00", cash, "Обед"),
        (today - timedelta(days=3), "Транспорт", "Такси", "420.00", card, None),
        (today - timedelta(days=4), "Транспорт", "Метро", "320.00", card, "Проездной"),
        (today - timedelta(days=5), "Развлечения", "Подписки", "399.00", card, "Музыка"),
        (today - timedelta(days=8), "Еда", "Доставка", "1250.00", card, "Ужин"),
        (today - timedelta(days=10), "Жильё", "Интернет", "700.00", card, None),
        (today - timedelta(days=14), "Жильё", "Коммуналка", "4800.00", card, "Июль"),
        (today - timedelta(days=15), "Еда", "Продукты", "3100.00", card, "Ашан"),
        (today - timedelta(days=18), "Развлечения", "Кино", "1200.00", cash, "С друзьями"),
        (today - timedelta(days=21), "Транспорт", "Бензин", "2800.00", card, "Полный бак"),
        (today - timedelta(days=25), "Жильё", "Аренда", "45000.00", card, "Август"),
    ]
    if not rich:
        expenses = [
            (today - timedelta(days=1), "Еда", "Продукты", "1800.00", card, None),
            (today - timedelta(days=3), "Еда", "Кафе", "650.00", cash, None),
            (today - timedelta(days=5), "Транспорт", "Такси", "500.00", card, None),
            (today - timedelta(days=9), "Транспорт", "Метро", "300.00", card, None),
            (today - timedelta(days=12), "Прочее", "Разное", "1500.00", card, "Хозтовары"),
        ]

    for day, cat_name, sub_name, value, wallet, comment in expenses:
        if cat_name not in expense_subs or sub_name not in expense_subs[cat_name]:
            continue
        ExpensesHistory.objects.create(
            project=project,
            date=day,
            value=Decimal(value),
            category=expense_cats[cat_name],
            subcategory=expense_subs[cat_name][sub_name],
            wallet=wallet,
            comment=comment or "",
        )

    TransactionsHistory.objects.create(
        project=project,
        date=today - timedelta(days=6),
        value=Decimal("10000.00"),
        source=card,
        aim=savings,
        comment="Отложить на отпуск",
    )
    if rich:
        TransactionsHistory.objects.create(
            project=project,
            date=today - timedelta(days=16),
            value=Decimal("3000.00"),
            source=card,
            aim=cash,
            comment="Снять наличные",
        )

    credit = Credit.objects.create(
        project=project,
        name="Кредит на телефон",
        credit_sum=Decimal("45000.00"),
    )
    CreditHistory.objects.create(
        project=project,
        credit=credit,
        date=today - timedelta(days=40),
        value=Decimal("5000.00"),
        balance=Decimal("40000.00"),
    )
    CreditHistory.objects.create(
        project=project,
        credit=credit,
        date=today - timedelta(days=10),
        value=Decimal("5000.00"),
        balance=Decimal("35000.00"),
    )

    plan_month = today.month
    plan_year = today.year
    plan_values = {
        "Еда": "25000.00",
        "Транспорт": "8000.00",
        "Жильё": "52000.00",
        "Развлечения": "5000.00",
        "Прочее": "4000.00",
    }
    for cat_name, cat in expense_cats.items():
        Planes.objects.create(
            project=project,
            year=plan_year,
            month=plan_month,
            category=cat,
            value=Decimal(plan_values.get(cat_name, "3000.00")),
        )

    return {
        "wallets": Wallet.objects.filter(project=project).count(),
        "income_categories": IncomeCategory.objects.filter(project=project).count(),
        "expense_categories": ExpensesCategory.objects.filter(project=project).count(),
        "expense_subcategories": ExpensesSubCategory.objects.filter(project=project).count(),
        "incomes": IncomeHistory.objects.filter(project=project).count(),
        "expenses": ExpensesHistory.objects.filter(project=project).count(),
        "transactions": TransactionsHistory.objects.filter(project=project).count(),
        "credits": Credit.objects.filter(project=project).count(),
        "credit_payments": CreditHistory.objects.filter(project=project).count(),
        "plans": Planes.objects.filter(project=project).count(),
    }


class Command(BaseCommand):
    help = "Заполняет проекты тестовыми категориями, доходами, расходами и связанными сущностями"

    @transaction.atomic
    def handle(self, *args, **options):
        projects = list(Project.objects.order_by("id"))
        if not projects:
            self.stderr.write("Нет проектов — сначала создайте хотя бы один проект.")
            return

        for index, project in enumerate(projects):
            _clear_project_accounting(project)
            stats = _seed_project(project, rich=(index == 0))
            self.stdout.write(self.style.SUCCESS(f"Проект «{project.name}» (id={project.id}):"))
            for key, value in stats.items():
                self.stdout.write(f"  {key}: {value}")
