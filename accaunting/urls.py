from django.urls import path, include
from accaunting.views import ExpensesHistoryRecordCreateView

urlpatterns = [
    path('expenses/create', ExpensesHistoryRecordCreateView.as_view())
]
