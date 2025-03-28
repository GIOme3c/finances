from django.contrib import admin
from accaunting.models import (
    IncomeCategory,
    ExpensesCategory,
    ExpensesSubCategory,
    Wallet,
    ExpensesHistory,
    IncomeHistory,
    TransactionsHistory,
    Credit,
    CreditHistory,
    Planes,
)

# Register your models here.

admin.site.register(IncomeCategory)
admin.site.register(ExpensesCategory)
admin.site.register(ExpensesSubCategory)
admin.site.register(Wallet)
admin.site.register(ExpensesHistory)
admin.site.register(IncomeHistory)
admin.site.register(TransactionsHistory)
admin.site.register(Credit)
admin.site.register(CreditHistory)
admin.site.register(Planes)
