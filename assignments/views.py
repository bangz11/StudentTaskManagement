from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from .models import Assignment


def home(request):
    return render(request, 'assignments/home.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not username or not email or not password:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('register')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)
        return redirect('dashboard')

    return render(request, 'assignments/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'assignments/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    assignments = Assignment.objects.filter(user=request.user)

    total_assignments = assignments.count()
    pending_assignments = assignments.filter(status='Pending').count()
    in_progress_assignments = assignments.filter(status='In Progress').count()
    completed_assignments = assignments.filter(status='Completed').count()
    high_priority_assignments = assignments.filter(priority='High').count()

    today = timezone.localdate()

    upcoming_assignments = assignments.filter(
        due_date__gte=today
    ).order_by('due_date')[:5]

    return render(request, 'assignments/dashboard.html', {
        'total_assignments': total_assignments,
        'pending_assignments': pending_assignments,
        'in_progress_assignments': in_progress_assignments,
        'completed_assignments': completed_assignments,
        'high_priority_assignments': high_priority_assignments,
        'upcoming_assignments': upcoming_assignments,
    })


def assignment_list(request):
    if not request.user.is_authenticated:
        return redirect('login')

    assignments = Assignment.objects.filter(user=request.user)

    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()
    priority = request.GET.get('priority', '').strip()
    sort = request.GET.get('sort', 'due_date').strip()

    if search:
        assignments = assignments.filter(
            title__icontains=search
        ) | assignments.filter(
            subject__icontains=search
        ) | assignments.filter(
            description__icontains=search
        )

    if status:
        assignments = assignments.filter(status=status)

    if priority:
        assignments = assignments.filter(priority=priority)

    if sort == 'title':
        assignments = assignments.order_by('title')
    elif sort == 'priority':
        assignments = assignments.order_by('priority', 'due_date')
    elif sort == 'status':
        assignments = assignments.order_by('status', 'due_date')
    elif sort == 'newest':
        assignments = assignments.order_by('-created_at')
    else:
        assignments = assignments.order_by('due_date')

    return render(request, 'assignments/assignment_list.html', {
        'assignments': assignments,
        'search': search,
        'selected_status': status,
        'selected_priority': priority,
        'selected_sort': sort,
    })


def add_assignment(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        Assignment.objects.create(
            user=request.user,
            title=request.POST.get('title'),
            subject=request.POST.get('subject'),
            description=request.POST.get('description'),
            due_date=request.POST.get('due_date'),
            priority=request.POST.get('priority'),
            status=request.POST.get('status')
        )

        messages.success(request, 'Assignment added successfully.')
        return redirect('assignment_list')

    return render(request, 'assignments/add_assignment.html')


def edit_assignment(request, assignment_id):
    if not request.user.is_authenticated:
        return redirect('login')

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        user=request.user
    )

    if request.method == 'POST':
        assignment.title = request.POST.get('title')
        assignment.subject = request.POST.get('subject')
        assignment.description = request.POST.get('description')
        assignment.due_date = request.POST.get('due_date')
        assignment.priority = request.POST.get('priority')
        assignment.status = request.POST.get('status')
        assignment.save()

        messages.success(request, 'Assignment updated successfully.')
        return redirect('assignment_list')

    return render(request, 'assignments/edit_assignment.html', {
        'assignment': assignment
    })


def delete_assignment(request, assignment_id):
    if not request.user.is_authenticated:
        return redirect('login')

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        user=request.user
    )

    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Assignment deleted successfully.')

    return redirect('assignment_list')
