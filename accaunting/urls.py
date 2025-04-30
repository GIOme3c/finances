from django.urls import path
from accaunting import views

urlpatterns = [
    path('<int:pr_pk>/expenses/create', views.ExpensesHistoryRecordCreateView.as_view(), name="expenses-create"),
    path('<int:pr_pk>/expenses/<int:pk>/update', views.ExpensesHistoryRecordUpdateView.as_view(), name="expenses-update"),
    path('<int:pr_pk>/expenses/list', views.ExpensesHistoryListView.as_view(), name="expenses-list"),
    path('<int:pr_pk>/expenses/<int:pk>/delete', views.ExpensesHistoryRecordDeleteView.as_view(), name="expenses-delete"),

    path('<int:pr_pk>/modal/category/create', views.ExpensesCategoryCreateView.as_view(), name="category-create-modal"),
    path('<int:pr_pk>/modal/subcategory/create', views.ExpensesSubCategoryCreateView.as_view(), name="subcategory-create-modal"),
]
