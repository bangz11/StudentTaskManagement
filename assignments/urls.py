from django.urls import path
from . import views
from .api_views import AssignmentListCreateAPI, AssignmentDetailAPI

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/add/', views.add_assignment, name='add_assignment'),
    path('assignments/<int:assignment_id>/edit/', views.edit_assignment, name='edit_assignment'),
    path('assignments/<int:assignment_id>/delete/', views.delete_assignment, name='delete_assignment'),

    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/students/', views.teacher_students, name='teacher_students'),
    path('teacher/students/<int:user_id>/', views.teacher_student_detail, name='teacher_student_detail'),

    path('api/assignments/', AssignmentListCreateAPI.as_view(), name='api_assignment_list'),
    path('api/assignments/<int:pk>/', AssignmentDetailAPI.as_view(), name='api_assignment_detail'),
]
