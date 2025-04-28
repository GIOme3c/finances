from django.http import JsonResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.views import View
from django.forms import DateInput, TextInput
from django.urls import reverse_lazy

from accaunting.forms import ExpensesCategoryModelForm, ExpensesSubCategoryModelForm
from accaunting.models import ExpensesHistory



class ExpensesHistoryRecordCreateView(CreateView):
    model = ExpensesHistory
    fields = "__all__"
    template_name = "accaunting/expenses_history_record_update.html"
    success_url = reverse_lazy('expenses-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date'].widget = DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'data-datepicker': ''
            }
        )
        form.fields['comment'].widget = TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите комментарий'}
        )
        return form
    

class ExpensesHistoryRecordUpdateView(UpdateView):
    model = ExpensesHistory
    fields = "__all__"
    template_name = "accaunting/expenses_history_record_update.html"
    success_url = reverse_lazy('expenses-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date'].widget = DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'data-datepicker': '',
            }
        )
        form.fields['comment'].widget = TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите комментарий'}
        )
        return form


class ExpensesHistoryListView(ListView):
    model = ExpensesHistory
    template_name = "accaunting/expenses_history_list.html"
    paginate_by = 15


class ExpensesHistoryRecordDeleteView(DeleteView):
    model = ExpensesHistory
    success_url = reverse_lazy('expenses-list')
    template_name = "accaunting/expenses_history_record_delete.html"


class ExpensesCategoryCreateView(View):
    def post(self, request):
        form = ExpensesCategoryModelForm(request.POST)
        if form.is_valid():
            category = form.save()
            return JsonResponse({
                'success': True,
                'id': category.id,
                'name': category.name
            })


class ExpensesSubCategoryCreateView(View):
    def post(self, request):
        form = ExpensesSubCategoryModelForm(request.POST)
        if form.is_valid():
            subcategory = form.save()
            return JsonResponse({
                'success': True,
                'id': subcategory.id,
                'name': subcategory.name
            })