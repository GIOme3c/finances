from django.db import models

from user_profile.models import Project
from user_profile.mixins import (
    ProjectRelatedMixin,
    DeactivatedMixin,
)


class IncomeCategory(DeactivatedMixin):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    name = models.CharField("Название", max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория дохода"
        verbose_name_plural = "Категории доходов"
        unique_together = (("project", "name"),)


class ExpensesCategory(DeactivatedMixin):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    name = models.CharField("Название", max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория трат"
        verbose_name_plural = "Категории трат"
        unique_together = (("project", "name"),)


class ExpensesSubCategory(DeactivatedMixin):
    name = models.CharField("Название", max_length=64)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    category = models.ForeignKey(ExpensesCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (("category", "name", "project"),)
        verbose_name = "Подкатегория трат"
        verbose_name_plural = "Подкатегории трат"


class Wallet(DeactivatedMixin):
    current_value = models.DecimalField("Текущий остаток", max_digits=15, decimal_places=2, default=0)
    is_keeping = models.BooleanField("Накопительный", default=False)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    name = models.CharField("Название", max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Cчёт"
        verbose_name_plural = "Cчёта"
        unique_together = (("project", "name"),)


class ExpensesHistory(ProjectRelatedMixin):
    date = models.DateField("Дата")
    value = models.DecimalField("Сумма", max_digits=15, decimal_places=2)
    category = models.ForeignKey(ExpensesCategory, on_delete=models.PROTECT, verbose_name='Категория')
    subcategory = models.ForeignKey(ExpensesSubCategory, on_delete=models.PROTECT, verbose_name='Подкатегория')
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, verbose_name='Счёт')
    comment = models.TextField("Описание", null=True, blank=True)

    def __str__(self):
        return str(self.date) + str(self.value) + str(self.category)

    class Meta:
        verbose_name = "История трат"
        verbose_name_plural = "История трат"


class IncomeHistory(ProjectRelatedMixin):
    date = models.DateField("Дата")
    value = models.DecimalField("Сумма", max_digits=15, decimal_places=2)
    category = models.ForeignKey(IncomeCategory, on_delete=models.PROTECT)
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT)
    comment = models.TextField("Описание", null=True, blank=True)

    def __str__(self):
        return str(self.date) + str(self.value) + str(self.category)

    class Meta:
        verbose_name = "История доходов"
        verbose_name_plural = "История доходов"


class TransactionsHistory(ProjectRelatedMixin):
    date = models.DateField("Дата")
    value = models.DecimalField("Сумма", max_digits=15, decimal_places=2)
    source = models.ForeignKey(Wallet, related_name="trans_sourse", on_delete=models.PROTECT)
    aim = models.ForeignKey(Wallet, related_name="aim_sourse", on_delete=models.PROTECT)
    comment = models.TextField("Описание", null=True, blank=True)

    def __str__(self):
        return str(self.date) + str(self.value) + str(self.source) + str(self.aim)

    class Meta:
        verbose_name = "История переводов"
        verbose_name_plural = "История переводов"


class Credit(DeactivatedMixin):
    credit_sum = models.DecimalField("Сумма", max_digits=15, decimal_places=2)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    name = models.CharField("Название", max_length=64)

    class Meta:
        verbose_name = "Кредит"
        verbose_name_plural = "Кредиты"
        unique_together = (("project", "name"),)


class CreditHistory(ProjectRelatedMixin):
    credit = models.ForeignKey(Credit, on_delete=models.PROTECT)
    date = models.DateField("Дата")
    value = models.DecimalField("Сумма", max_digits=15, decimal_places=2)
    balance = models.DecimalField("Остаток", max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = "История оплаты кредитов"
        verbose_name_plural = "История оплаты кредитов"


class Planes(ProjectRelatedMixin):
    year = models.PositiveIntegerField("Год")
    month = models.PositiveIntegerField("Месяц")
    category = models.ForeignKey(ExpensesCategory, on_delete=models.PROTECT)
    value = models.DecimalField("Сумма", max_digits=15, decimal_places=2)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "План расходов"
        verbose_name_plural = "Планы расходов"
        unique_together = (("year", "month", "category", "project"),)

