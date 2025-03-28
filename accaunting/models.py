from django.db import models


class IncomeCategory(models.Model):
    name = models.CharField("Название", max_length=64, unique=True)
    is_active = models.BooleanField("Актуальная", default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория дохода"
        verbose_name_plural = "Категории доходов"


class ExpensesCategory(models.Model):
    name = models.CharField("Название", max_length=64, unique=True)
    is_active = models.BooleanField("Актуальная", default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория трат"
        verbose_name_plural = "Категории трат"


class ExpensesSubCategory(models.Model):
    category = models.ForeignKey(ExpensesCategory, on_delete=models.CASCADE)
    name = models.CharField("Название", max_length=64)
    is_active = models.BooleanField("Актуальная", default=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (("category", "name"),)
        verbose_name = "Подкатегория трат"
        verbose_name_plural = "Подкатегории трат"


class Wallet(models.Model):
    name = models.CharField("Название", max_length=64)
    current_value = models.DecimalField("Текущий остаток", max_digits=15, decimal_places=2, default=0)
    is_keeping = models.BooleanField("Накопительный", default=False)
    is_active = models.BooleanField("Актуальный", default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Cчёт"
        verbose_name_plural = "Cчёта"


class ExpensesHistory(models.Model):
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


class IncomeHistory(models.Model):
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


class TransactionsHistory(models.Model):
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


class Credit(models.Model):
    name = models.CharField("Название", max_length=64)
    credit_sum = models.DecimalField("Сумма", max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = "Кредит"
        verbose_name_plural = "Кредиты"


class CreditHistory(models.Model):
    credit = models.ForeignKey(Credit, on_delete=models.PROTECT)
    date = models.DateField("Дата")
    value = models.DecimalField("Сумма", max_digits=15, decimal_places=2)
    balance = models.DecimalField("Остаток", max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = "История оплаты кредитов"
        verbose_name_plural = "История оплаты кредитов"


class Planes(models.Model):
    year = models.PositiveIntegerField("Год")
    month = models.PositiveIntegerField("Месяц")
    category = models.ForeignKey(ExpensesCategory, on_delete=models.PROTECT)
    value = models.DecimalField("Сумма", max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = "План расходов"
        verbose_name_plural = "Планы расходов"
