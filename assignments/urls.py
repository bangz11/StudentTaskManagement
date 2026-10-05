from django.urls import path
from . import views
from .api_views import AssignmentListCreateAPI, AssignmentDetailAPI

urlpatterns = [
    path('', views.home, name='home'),

    path('login/', views.login_view, name='login'),
    path('student/login/', views.student_login, name='student_login'),
    path('teacher/login/', views.teacher_login, name='teacher_login'),

    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('explore/', views.explore, name='explore'),

    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/add/', views.add_assignment, name='add_assignment'),
    path('assignments/<int:assignment_id>/edit/', views.edit_assignment, name='edit_assignment'),
    path('assignments/<int:assignment_id>/delete/', views.delete_assignment, name='delete_assignment'),
    path('assignments/<int:assignment_id>/remove-file/', views.remove_assignment_file, name='remove_assignment_file'),

    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/students/', views.teacher_students, name='teacher_students'),
    path('teacher/students/<int:user_id>/', views.teacher_student_detail, name='teacher_student_detail'),
    path('teacher/students/<int:user_id>/assign/', views.teacher_create_assignment, name='teacher_create_assignment'),
    
    path(
    'teacher/students/<int:user_id>/add-assignment/',
    views.teacher_add_assignment,
    name='teacher_add_assignment'
),

    path('api/assignments/', AssignmentListCreateAPI.as_view(), name='api_assignment_list'),
    path('api/assignments/<int:pk>/', AssignmentDetailAPI.as_view(), name='api_assignment_detail'),
]
