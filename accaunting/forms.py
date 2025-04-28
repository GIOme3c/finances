from django import forms
from accaunting.models import ExpensesCategory, ExpensesSubCategory


class ExpensesCategoryModelForm(forms.ModelForm):
    class Meta:
        model = ExpensesCategory
        fields = "__all__"


class ExpensesSubCategoryModelForm(forms.ModelForm):
    class Meta:
        model = ExpensesSubCategory
        fields = "__all__"