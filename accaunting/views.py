from django.views.generic.edit import CreateView  # DeleteView, UpdateView
from accaunting.models import ExpensesHistory
from django.forms import DateInput, TextInput


class ExpensesHistoryRecordCreateView(CreateView):
    model = ExpensesHistory
    fields = "__all__"
    template_name = "accaunting/expenses_history_record_create.html"
    # success_url = 

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date'].widget = DateInput(
            attrs={'type': 'date', 'class': 'form-control'}, 
            format='%d/%m/%Y',
        )
        form.fields['comment'].widget = TextInput(attrs={'class': 'form-control'})
        return form