from django.urls import path
from accaunting import views

urlpatterns = [
    path('expenses/create', views.ExpensesHistoryRecordCreateView.as_view(), name="expenses-create"),
    path('expenses/<int:pk>/update', views.ExpensesHistoryRecordUpdateView.as_view(), name="expenses-update"),
    path('expenses/list', views.ExpensesHistoryListView.as_view(), name="expenses-list"),
    path('expenses/<int:pk>/delete', views.ExpensesHistoryRecordDeleteView.as_view(), name="expenses-delete"),

    path('modal/category/create', views.ExpensesCategoryCreateView.as_view(), name="category-create-modal"),
    path('modal/subcategory/create', views.ExpensesSubCategoryCreateView.as_view(), name="subcategory-create-modal"),
]
