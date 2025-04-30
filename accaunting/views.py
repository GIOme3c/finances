from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views import View
from django.forms import DateInput, TextInput
from django.urls import reverse_lazy

from accaunting.forms import ExpensesCategoryModelForm, ExpensesSubCategoryModelForm
from accaunting.models import ExpensesHistory



class ExpensesHistoryRecordCreateView(CreateView):
    model = ExpensesHistory
    fields = "__all__"
    template_name = "accaunting/expenses_history_record_update.html"
    # success_url = reverse_lazy('expenses-list')

    def post(self, request, *args, **kwargs):
        self.success_url = reverse_lazy('expenses-list', kwargs['pr_pk'])
        print(self.success_url)
        return super().post(request, *args, **kwargs)

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
    
    def form_valid(self, form):
        form.instance.project = self.kwargs["pr_pk"]
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pr_pk"] = self.kwargs["pr_pk"]
        return context


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
    
    def form_valid(self, form):
        form.instance.project = self.kwargs["pr_pk"]
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pr_pk"] = self.kwargs["pr_pk"]
        return context


class ExpensesHistoryListView(ListView):
    model = ExpensesHistory
    template_name = "accaunting/expenses_history_list.html"
    paginate_by = 15

    def get_queryset(self):
        return super().get_queryset().filter(project__id=self.kwargs['pr_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pr_pk"] = self.kwargs["pr_pk"]
        return context
    

class ExpensesHistoryRecordDeleteView(DeleteView):
    model = ExpensesHistory
    success_url = reverse_lazy('expenses-list')
    template_name = "accaunting/expenses_history_record_delete.html"


class ExpensesCategoryCreateView(View):
    def post(self, request, pr_pk):
        form_data = request.POST.dict()
        form_data["project"] = pr_pk
        form = ExpensesCategoryModelForm(form_data)
        if form.is_valid():
            category = form.save()
            return JsonResponse({
                'success': True,
                'id': category.id,
                'name': category.name
            })
    

class ExpensesSubCategoryCreateView(View):
    def post(self, request, pr_pk):
        form_data = request.POST.dict()
        form_data["project"] = pr_pk
        form = ExpensesSubCategoryModelForm(form_data)
        if form.is_valid():
            subcategory = form.save()
            return JsonResponse({
                'success': True,
                'id': subcategory.id,
                'name': subcategory.name
            })
