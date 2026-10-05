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
            if user.is_staff:
                return redirect('teacher_dashboard')
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
        return redirect("login")

    messages.info(request, "Assignments are created by your teacher.")
    return redirect("assignment_list")


def edit_assignment(request, assignment_id):
    if not request.user.is_authenticated:
        return redirect("login")

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        user=request.user
    )

    if request.method == "POST":
        status = request.POST.get("status")

        if status in ["Pending", "In Progress", "Completed"]:
            assignment.status = status
            assignment.save(update_fields=["status", "updated_at"])
            messages.success(request, "Assignment progress updated successfully.")
        else:
            messages.error(request, "Invalid status.")

        return redirect("assignment_list")

    return render(request, "assignments/edit_assignment.html", {
        "assignment": assignment
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


from django.contrib.auth.decorators import user_passes_test

def teacher_required(view_func):
    return user_passes_test(
        lambda user: user.is_authenticated and user.is_staff,
        login_url='teacher_login'
    )(view_func)


@teacher_required
def teacher_dashboard(request):
    students = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).order_by('username')

    for student in students:
        student.assignment_count = Assignment.objects.filter(
            user=student
        ).count()

        student.completed_count = Assignment.objects.filter(
            user=student,
            status='Completed'
        ).count()

        student.pending_count = Assignment.objects.filter(
            user=student,
            status='Pending'
        ).count()

    total_students = students.count()
    total_assignments = Assignment.objects.count()
    completed_assignments = Assignment.objects.filter(status='Completed').count()
    pending_assignments = Assignment.objects.filter(status='Pending').count()

    return render(request, 'assignments/teacher_dashboard.html', {
        'students': students,
        'total_students': total_students,
        'total_assignments': total_assignments,
        'completed_assignments': completed_assignments,
        'pending_assignments': pending_assignments,
    })


@teacher_required
def teacher_students(request):
    search = request.GET.get('search', '').strip()

    students = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).order_by('username')

    if search:
        students = students.filter(
            username__icontains=search
        ) | students.filter(
            email__icontains=search
        )

    return render(request, 'assignments/teacher_students.html', {
        'students': students,
        'search': search,
    })


@teacher_required
def teacher_student_detail(request, user_id):
    student = get_object_or_404(
        User,
        id=user_id,
        is_staff=False,
        is_superuser=False
    )

    assignments = Assignment.objects.filter(
        user=student
    ).order_by('due_date')

    return render(request, 'assignments/teacher_student_detail.html', {
        'student': student,
        'assignments': assignments,
    })


def explore(request):
    return render(request, 'assignments/explore.html')



def student_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('teacher_dashboard')
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and not user.is_staff:
            login(request, user)
            return redirect('dashboard')

        messages.error(
            request,
            'Invalid student username or password.'
        )

    return render(request, 'assignments/student_login.html')


def teacher_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('teacher_dashboard')
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('teacher_dashboard')

        messages.error(
            request,
            'Teacher access denied. Please use a teacher account.'
        )

    return render(request, 'assignments/teacher_login.html')
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Assignment

def remove_assignment_file(request, assignment_id):
    if not request.user.is_authenticated:
        return redirect('login')

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        user=request.user
    )

    if request.method == 'POST':
        if assignment.assignment_file:
            assignment.assignment_file.delete(save=False)

        assignment.assignment_file = None
        assignment.file_text = ''
        assignment.save(update_fields=['assignment_file', 'file_text'])

        messages.success(request, 'Assignment file removed successfully.')

    return redirect('assignment_list')

@teacher_required
def teacher_add_assignment(request, user_id):
    student = get_object_or_404(
        User,
        id=user_id,
        is_staff=False,
        is_superuser=False
    )

    if request.method == 'POST':
        uploaded_file = request.FILES.get('assignment_file')

        title = request.POST.get('title', '').strip()
        subject = request.POST.get('subject', '').strip()
        description = request.POST.get('description', '').strip()
        due_date = request.POST.get('due_date')
        priority = request.POST.get('priority', 'Medium')
        status = request.POST.get('status', 'Pending')

        if uploaded_file:
            allowed_extensions = ['.pdf', '.docx', '.png', '.jpg', '.jpeg']
            extension = Path(uploaded_file.name).suffix.lower()

            if extension not in allowed_extensions:
                messages.error(
                    request,
                    'Please upload a PDF, DOCX, JPG, JPEG, or PNG file.'
                )
                return redirect(
                    'teacher_add_assignment',
                    user_id=student.id
                )

            if uploaded_file.size > 10 * 1024 * 1024:
                messages.error(
                    request,
                    'File must be smaller than 10 MB.'
                )
                return redirect(
                    'teacher_add_assignment',
                    user_id=student.id
                )

        if not title or not subject or not due_date:
            messages.error(
                request,
                'Please fill in the title, subject, and due date.'
            )
            return redirect(
                'teacher_add_assignment',
                user_id=student.id
            )

        file_text = ''

        if uploaded_file:
            file_text = extract_file_text(uploaded_file)

        Assignment.objects.create(
            user=student,
            assigned_by=request.user,
            title=title,
            subject=subject,
            description=description,
            assignment_file=uploaded_file,
            file_text=file_text,
            due_date=due_date,
            priority=priority,
            status=status
        )

        messages.success(
            request,
            f'Assignment created for {student.username}.'
        )

        return redirect(
            'teacher_student_detail',
            user_id=student.id
        )

    return render(
        request,
        'assignments/teacher_add_assignment.html',
        {
            'student': student
        }
    )



@teacher_required
def teacher_create_assignment(request, user_id):
    student = get_object_or_404(
        User,
        id=user_id,
        is_staff=False,
        is_superuser=False
    )

    if request.method == 'POST':
        uploaded_file = request.FILES.get('assignment_file')

        title = request.POST.get('title', '').strip()
        subject = request.POST.get('subject', '').strip()
        description = request.POST.get('description', '').strip()
        due_date = request.POST.get('due_date')
        priority = request.POST.get('priority', 'Medium')
        status = request.POST.get('status', 'Pending')

        file_text = ''

        if uploaded_file:
            allowed_extensions = ['.pdf', '.docx', '.png', '.jpg', '.jpeg']
            extension = Path(uploaded_file.name).suffix.lower()

            if extension not in allowed_extensions:
                messages.error(
                    request,
                    'Please upload a PDF, DOCX, JPG, JPEG, or PNG file.'
                )
                return redirect('teacher_create_assignment', user_id=student.id)

            if uploaded_file.size > 10 * 1024 * 1024:
                messages.error(
                    request,
                    'File must be smaller than 10 MB.'
                )
                return redirect('teacher_create_assignment', user_id=student.id)

            file_text = extract_file_text(uploaded_file)

        if not title or not subject or not due_date:
            messages.error(
                request,
                'Please fill in the title, subject, and deadline.'
            )
            return redirect('teacher_create_assignment', user_id=student.id)

        Assignment.objects.create(
            user=student,
            assigned_by=request.user,
            title=title,
            subject=subject,
            description=description,
            due_date=due_date,
            priority=priority,
            status=status,
            assignment_file=uploaded_file,
            file_text=file_text
        )

        messages.success(
            request,
            f'Assignment assigned to {student.username} successfully.'
        )

        return redirect(
            'teacher_student_detail',
            user_id=student.id
        )

    return render(request, 'assignments/teacher_create_assignment.html', {
        'student': student
    })
