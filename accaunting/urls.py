from django.urls import path
from accaunting import views

urlpatterns = [
    path('<int:pr_pk>/expenses/create', views.ExpensesHistoryRecordCreateView.as_view(), name="expenses-create"),
    path('<int:pr_pk>/expenses/<int:pk>/update', views.ExpensesHistoryRecordUpdateView.as_view(), name="expenses-update"),
    path('<int:pr_pk>/expenses/list', views.ExpensesHistoryListView.as_view(), name="expenses-list"),
    path('<int:pr_pk>/expenses/<int:pk>/delete', views.ExpensesHistoryRecordDeleteView.as_view(), name="expenses-delete"),

    path('<int:pr_pk>/income/create', views.IncomeHistoryRecordCreateView.as_view(), name="income-create"),
    path('<int:pr_pk>/income/<int:pk>/update', views.IncomeHistoryRecordUpdateView.as_view(), name="income-update"),
    path('<int:pr_pk>/income/list', views.IncomeHistoryListView.as_view(), name="income-list"),
    path('<int:pr_pk>/income/<int:pk>/delete', views.IncomeHistoryRecordDeleteView.as_view(), name="income-delete"),

    path('<int:pr_pk>/modal/category/create', views.ExpensesCategoryCreateView.as_view(), name="category-create-modal"),
    path('<int:pr_pk>/modal/subcategory/create', views.ExpensesSubCategoryCreateView.as_view(), name="subcategory-create-modal"),
    path('<int:pr_pk>/modal/income-category/create', views.IncomeCategoryCreateView.as_view(), name="income-category-create-modal"),
    path('<int:pr_pk>/wallets/create', views.WalletCreateView.as_view(), name="wallet-create"),

    path('<int:pr_pk>/transfers/create', views.TransactionsHistoryRecordCreateView.as_view(), name="transfers-create"),
    path('<int:pr_pk>/transfers/<int:pk>/update', views.TransactionsHistoryRecordUpdateView.as_view(), name="transfers-update"),
    path('<int:pr_pk>/transfers/list', views.TransactionsHistoryListView.as_view(), name="transfers-list"),
    path('<int:pr_pk>/transfers/<int:pk>/delete', views.TransactionsHistoryRecordDeleteView.as_view(), name="transfers-delete"),
]
