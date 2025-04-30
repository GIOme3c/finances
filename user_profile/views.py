from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy

from user_profile.models import Project
from accaunting import models as acc_models



def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический вход после регистрации
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')  # Замените 'home' на имя вашего URL
        else:
            messages.error(request, 'Ошибка регистрации. Проверьте данные.')
    else:
        form = UserCreationForm()

    return render(request, 'profile/register.html', {'form': form})


def user_profile(request):
    if (request.user.is_authenticated):
        profile = request.user.profile
        context = {
            "projects": profile.all_projects
        }
        print(context["projects"][0].members.all())
        print(context["projects"][0].name)
        return render(request, 'profile/profile.html', context)
    else:
        return redirect('login')


class ProjectCreateView(CreateView):
    model = Project
    fields = ["name", "members"]
    template_name = "profile/project_update.html"
    success_url = reverse_lazy('profile')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['members'].queryset = form.fields['members'].queryset.exclude(id=self.request.user.profile.id)
        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user.profile
        return super().form_valid(form)


class ProjectUpdateView(UpdateView):
    model = Project
    fields = ["name", "members", "is_active"]
    template_name = "profile/project_update.html"
    success_url = reverse_lazy('profile')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['members'].queryset = form.fields['members'].queryset.exclude(id=self.request.user.profile.id)
        return form
    

class ProjectDeleteView(DeleteView):
    model = Project
    template_name = "profile/project_delete.html"
    success_url = reverse_lazy('profile')


class ProjectDetailView(DetailView):
    model = Project
    template_name = "profile/project_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = kwargs["object"]
        context["expenses"] = acc_models.ExpensesHistory.objects.filter(project=project)[:10]
        context["income"] = acc_models.IncomeHistory.objects.filter(project=project)[:10]
        return context
    
