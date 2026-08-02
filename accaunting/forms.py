from django import forms
from django.utils import timezone

from accaunting.models import (
    ExpensesCategory,
    ExpensesHistory,
    ExpensesSubCategory,
    IncomeCategory,
    IncomeHistory,
    TransactionsHistory,
    Wallet,
)


class ExpensesCategoryModelForm(forms.ModelForm):
    class Meta:
        model = ExpensesCategory
        fields = "__all__"


class ExpensesSubCategoryModelForm(forms.ModelForm):
    class Meta:
        model = ExpensesSubCategory
        fields = "__all__"


class IncomeCategoryModelForm(forms.ModelForm):
    class Meta:
        model = IncomeCategory
        fields = "__all__"


class ExpensesHistoryForm(forms.ModelForm):
    class Meta:
        model = ExpensesHistory
        fields = [
            "date",
            "value",
            "category",
            "subcategory",
            "wallet",
            "comment",
        ]

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project

        self.fields["category"].required = True
        self.fields["subcategory"].required = True
        self.fields["category"].error_messages["required"] = "Выберите категорию"
        self.fields["subcategory"].error_messages["required"] = "Выберите подкатегорию"
        self.fields["date"].input_formats = ["%d.%m.%Y", "%Y-%m-%d"]

        if project is not None:
            self.fields["category"].queryset = ExpensesCategory.objects.filter(
                project=project
            ).order_by("name")
            self.fields["subcategory"].queryset = ExpensesSubCategory.objects.filter(
                project=project
            ).select_related("category").order_by("name")
            self.fields["wallet"].queryset = self.fields["wallet"].queryset.filter(
                project=project
            ).order_by("name")

            if not self.is_bound and not self.initial.get("wallet") and not (
                self.instance and self.instance.wallet_id
            ):
                first_wallet = self.fields["wallet"].queryset.first()
                if first_wallet is not None:
                    self.initial["wallet"] = first_wallet.pk

        if not self.is_bound and not self.initial.get("date") and not (
            self.instance and self.instance.pk and self.instance.date
        ):
            self.initial["date"] = timezone.localdate().strftime("%d.%m.%Y")

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        subcategory = cleaned_data.get("subcategory")

        if category and subcategory and subcategory.category_id != category.id:
            self.add_error(
                "subcategory",
                "Подкатегория не относится к выбранной категории",
            )

        if self.project is not None:
            if category and category.project_id != self.project.id:
                self.add_error("category", "Категория не принадлежит этому проекту")
            if subcategory and subcategory.project_id != self.project.id:
                self.add_error(
                    "subcategory",
                    "Подкатегория не принадлежит этому проекту",
                )

        return cleaned_data


class IncomeHistoryForm(forms.ModelForm):
    class Meta:
        model = IncomeHistory
        fields = [
            "date",
            "value",
            "category",
            "wallet",
            "comment",
        ]

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project

        self.fields["category"].required = True
        self.fields["category"].error_messages["required"] = "Выберите категорию"
        self.fields["date"].input_formats = ["%d.%m.%Y", "%Y-%m-%d"]

        if project is not None:
            self.fields["category"].queryset = IncomeCategory.objects.filter(
                project=project
            ).order_by("name")
            self.fields["wallet"].queryset = self.fields["wallet"].queryset.filter(
                project=project
            ).order_by("name")

            if not self.is_bound and not self.initial.get("wallet") and not (
                self.instance and self.instance.wallet_id
            ):
                first_wallet = self.fields["wallet"].queryset.first()
                if first_wallet is not None:
                    self.initial["wallet"] = first_wallet.pk

        if not self.is_bound and not self.initial.get("date") and not (
            self.instance and self.instance.pk and self.instance.date
        ):
            self.initial["date"] = timezone.localdate().strftime("%d.%m.%Y")

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")

        if self.project is not None and category and category.project_id != self.project.id:
            self.add_error("category", "Категория не принадлежит этому проекту")

        return cleaned_data


class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ["name", "current_value", "is_keeping"]

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project
        self.fields["name"].required = True
        self.fields["name"].error_messages["required"] = "Введите название счёта"
        self.fields["current_value"].required = False
        self.fields["current_value"].label = "Начальный остаток"
        if not self.is_bound and not self.initial.get("current_value"):
            if not (self.instance and self.instance.pk):
                self.initial["current_value"] = "0.00"

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise forms.ValidationError("Введите название счёта")
        if self.project is not None:
            qs = Wallet.objects.filter(project=self.project, name=name)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Счёт с таким названием уже есть")
        return name

    def save(self, commit=True):
        wallet = super().save(commit=False)
        if self.project is not None:
            wallet.project = self.project
        if wallet.current_value is None:
            wallet.current_value = 0
        if commit:
            wallet.save()
        return wallet


class TransactionsHistoryForm(forms.ModelForm):
    class Meta:
        model = TransactionsHistory
        fields = [
            "date",
            "value",
            "source",
            "aim",
            "comment",
        ]

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project

        self.fields["source"].label = "Откуда"
        self.fields["aim"].label = "Куда"
        self.fields["source"].required = True
        self.fields["aim"].required = True
        self.fields["value"].required = True
        self.fields["source"].error_messages["required"] = "Выберите счёт списания"
        self.fields["aim"].error_messages["required"] = "Выберите счёт зачисления"
        self.fields["date"].input_formats = ["%d.%m.%Y", "%Y-%m-%d"]

        if project is not None:
            wallets = Wallet.objects.filter(project=project, is_active=True).order_by("name")
            self.fields["source"].queryset = wallets
            self.fields["aim"].queryset = wallets

            if not self.is_bound:
                wallet_list = list(wallets[:2])
                if not self.initial.get("source") and not (
                    self.instance and self.instance.source_id
                ):
                    if wallet_list:
                        self.initial["source"] = wallet_list[0].pk
                if not self.initial.get("aim") and not (
                    self.instance and self.instance.aim_id
                ):
                    if len(wallet_list) > 1:
                        self.initial["aim"] = wallet_list[1].pk
                    elif wallet_list:
                        self.initial["aim"] = wallet_list[0].pk

        if not self.is_bound and not self.initial.get("date") and not (
            self.instance and self.instance.pk and self.instance.date
        ):
            self.initial["date"] = timezone.localdate().strftime("%d.%m.%Y")

    def clean_value(self):
        value = self.cleaned_data.get("value")
        if value is not None and value <= 0:
            raise forms.ValidationError("Сумма должна быть больше нуля")
        return value

    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get("source")
        aim = cleaned_data.get("aim")

        if source and aim and source.pk == aim.pk:
            self.add_error("aim", "Счета списания и зачисления должны отличаться")

        if self.project is not None:
            if source and source.project_id != self.project.id:
                self.add_error("source", "Счёт не принадлежит этому проекту")
            if aim and aim.project_id != self.project.id:
                self.add_error("aim", "Счёт не принадлежит этому проекту")

        return cleaned_data
