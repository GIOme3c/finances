
from django.contrib.auth import views as auth_views
from django.urls import path
from user_profile import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='profile/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.user_profile, name='profile'),

    path('project/create', views.ProjectCreateView.as_view(), name='project-create'),
    path('project/<int:pk>/update', views.ProjectUpdateView.as_view(), name='project-update'),
    path('project/<int:pk>/delete', views.ProjectDeleteView.as_view(), name='project-delete'),
    path('project/<int:pk>', views.ProjectDetailView.as_view(), name='project-detail')
]