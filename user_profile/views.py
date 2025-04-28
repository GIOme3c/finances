from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from user_profile.models import Project



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

    # def get_form(self, form_class=None):
    #     form = super().get_form(form_class)
    #     form.fields['date'].widget = DateInput(
    #         attrs={
    #             'type': 'date',
    #             'class': 'form-control',
    #             'data-datepicker': ''
    #         }
    #     )
    #     form.fields['comment'].widget = TextInput(
    #         attrs={'class': 'form-control', 'placeholder': 'Введите комментарий'}
    #     )
    #     return form