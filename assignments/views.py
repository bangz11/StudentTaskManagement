from pathlib import Path

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Assignment


# ============================================================
# GENERAL
# ============================================================

def home(request):
    return render(request, 'assignments/home.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

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


# ============================================================
# STUDENT
# ============================================================

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.is_staff:
        return redirect('teacher_dashboard')

    assignments = Assignment.objects.filter(
        user=request.user
    ).order_by('due_date')

    total_assignments = assignments.count()
    pending_assignments = assignments.filter(
        status='Pending'
    ).count()
    in_progress_assignments = assignments.filter(
        status='In Progress'
    ).count()
    completed_assignments = assignments.filter(
        status='Completed'
    ).count()
    high_priority_assignments = assignments.filter(
        priority='High'
    ).count()

    today = timezone.localdate()

    upcoming_assignments = assignments.filter(
        due_date__gte=today
    ).order_by('due_date')[:5]

    return render(request, 'assignments/dashboard.html', {
        'total_assignments': total_assignments,
        'pending_assignments': pending_assignments,
            'assignments': Assignment.objects.filter(assigned_by=request.user).order_by('-created_at'),
        'in_progress_assignments': in_progress_assignments,
        'completed_assignments': completed_assignments,
        'high_priority_assignments': high_priority_assignments,
        'upcoming_assignments': upcoming_assignments,
    })


def assignment_list(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.is_staff:
        return redirect('teacher_dashboard')

    assignments = Assignment.objects.filter(
        user=request.user
    )

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

    if request.user.is_staff:
        return redirect('teacher_dashboard')

    messages.info(
        request,
        'Assignments are created and assigned by your teacher.'
    )
    return redirect('assignment_list')


def edit_assignment(request, assignment_id):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.is_staff:
        return redirect('teacher_dashboard')

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        user=request.user
    )

    if request.method == 'POST':
        status = request.POST.get('status')

        if status in ['Pending', 'In Progress', 'Completed']:
            assignment.status = status
            assignment.save(
                update_fields=['status', 'updated_at']
            )

            messages.success(
                request,
                'Assignment progress updated successfully.'
            )
        else:
            messages.error(request, 'Invalid status.')

        return redirect('assignment_list')

    return render(
        request,
        'assignments/edit_assignment.html',
        {'assignment': assignment}
    )


def delete_assignment(request, assignment_id):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.is_staff:
        return redirect('teacher_dashboard')

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        user=request.user
    )

    if request.method == 'POST':
        assignment.delete()
        messages.success(
            request,
            'Assignment deleted successfully.'
        )

    return redirect('assignment_list')


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
        assignment.save(
            update_fields=['assignment_file', 'file_text']
        )

        messages.success(
            request,
            'Assignment file removed successfully.'
        )

    return redirect('assignment_list')


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

    return render(
        request,
        'assignments/student_login.html'
    )


# ============================================================
# TEACHER ACCESS
# ============================================================

def teacher_required(view_func):
    return user_passes_test(
        lambda user: user.is_authenticated and user.is_staff,
        login_url='teacher_login'
    )(view_func)


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

    return render(
        request,
        'assignments/teacher_login.html'
    )


# ============================================================
# TEACHER DASHBOARD
# ============================================================

@teacher_required
def teacher_dashboard(request):
    students = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).order_by('username')

    total_students = students.count()
    total_assignments = Assignment.objects.filter(
        assigned_by=request.user
    ).count()

    completed_assignments = Assignment.objects.filter(
        assigned_by=request.user,
        status='Completed'
    ).count()

    pending_assignments = Assignment.objects.filter(
        assigned_by=request.user,
        status='Pending'
    ).count()

    for student in students:
        student.assignment_count = Assignment.objects.filter(
            user=student,
            assigned_by=request.user
        ).count()

        student.completed_count = Assignment.objects.filter(
            user=student,
            assigned_by=request.user,
            status='Completed'
        ).count()

        student.pending_count = Assignment.objects.filter(
            user=student,
            assigned_by=request.user,
            status='Pending'
        ).count()

    return render(
        request,
        'assignments/teacher_dashboard.html',
        {
            'students': students,
            'total_students': total_students,
            'total_assignments': total_assignments,
            'completed_assignments': completed_assignments,
            'pending_assignments': pending_assignments,
            'assignments': Assignment.objects.filter(assigned_by=request.user).order_by('-created_at'),
        }
    )


# ============================================================
# TEACHER STUDENTS
# ============================================================

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

    return render(
        request,
        'assignments/teacher_students.html',
        {
            'students': students,
            'search': search,
        }
    )


@teacher_required
def teacher_student_detail(request, user_id):
    student = get_object_or_404(
        User,
        id=user_id,
        is_staff=False,
        is_superuser=False
    )

    assignments = Assignment.objects.filter(
        user=student,
        assigned_by=request.user
    ).order_by('due_date')

    return render(
        request,
        'assignments/teacher_student_detail.html',
        {
            'student': student,
            'assignments': assignments,
        }
    )


# ============================================================
# TEACHER CREATE ASSIGNMENT
# ============================================================

@teacher_required
def teacher_create_assignment(request, user_id=None):
    students = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).order_by('username')

    selected_student = None

    if user_id:
        selected_student = get_object_or_404(
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

        selected_ids = request.POST.getlist('students')

        if not selected_ids and user_id:
            selected_ids = [str(user_id)]

        if not title or not subject or not due_date:
            messages.error(
                request,
                'Please fill in the title, subject, and deadline.'
            )
            return redirect(
                'teacher_create_assignment',
                user_id=user_id
            )

        if not selected_ids:
            messages.error(
                request,
                'Please select at least one student.'
            )
            return redirect(
                'teacher_create_assignment',
                user_id=user_id
            )

        if uploaded_file:
            allowed_extensions = [
                '.pdf',
                '.docx',
                '.png',
                '.jpg',
                '.jpeg'
            ]

            extension = Path(
                uploaded_file.name
            ).suffix.lower()

            if extension not in allowed_extensions:
                messages.error(
                    request,
                    'Please upload a PDF, DOCX, JPG, JPEG, or PNG file.'
                )
                return redirect(
                    'teacher_create_assignment',
                    user_id=user_id
                )

            if uploaded_file.size > 10 * 1024 * 1024:
                messages.error(
                    request,
                    'File must be smaller than 10 MB.'
                )
                return redirect(
                    'teacher_create_assignment',
                    user_id=user_id
                )

        selected_students = students.filter(
            id__in=selected_ids
        )

        for student in selected_students:
            file_for_student = uploaded_file

            if uploaded_file and selected_students.count() > 1:
                uploaded_file.seek(0)

            Assignment.objects.create(
                user=student,
                assigned_by=request.user,
                title=title,
                subject=subject,
                description=description,
                due_date=due_date,
                priority=priority,
                status=status,
                assignment_file=file_for_student,
                file_text=''
            )

        messages.success(
            request,
            f'Assignment assigned to {selected_students.count()} student(s) successfully.'
        )

        if selected_student:
            return redirect(
                'teacher_student_detail',
                user_id=selected_student.id
            )

        return redirect('teacher_students')

    return render(
        request,
        'assignments/teacher_create_assignment.html',
        {
            'student': selected_student,
            'students': students
        }
    )

# Keep the old URL working by sending it to the new teacher flow.
@teacher_required
def teacher_add_assignment(request, user_id):
    return teacher_create_assignment(
        request,
        user_id
    )


# ============================================================
# EXPLORE
# ============================================================

def explore(request):
    return render(
        request,
        'assignments/explore.html'
    )
# ============================================================
# STUDENT SUBMISSION
# ============================================================

def submit_assignment(request, assignment_id):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.is_staff:
        return redirect('teacher_dashboard')

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        user=request.user
    )

    if request.method == 'POST':
        uploaded_file = request.FILES.get('submission_file')

        if not uploaded_file:
            messages.error(
                request,
                'Please select a file to submit.'
            )
            return redirect('assignment_list')

        allowed_extensions = [
            '.pdf',
            '.docx',
            '.png',
            '.jpg',
            '.jpeg'
        ]

        extension = Path(
            uploaded_file.name
        ).suffix.lower()

        if extension not in allowed_extensions:
            messages.error(
                request,
                'Please upload a PDF, DOCX, JPG, JPEG, or PNG file.'
            )
            return redirect('assignment_list')

        if uploaded_file.size > 10 * 1024 * 1024:
            messages.error(
                request,
                'File must be smaller than 10 MB.'
            )
            return redirect('assignment_list')

        assignment.submission_file = uploaded_file
        assignment.submission_status = 'Submitted'
        assignment.submitted_at = timezone.now()

        assignment.save(
            update_fields=[
                'submission_file',
                'submission_status',
                'submitted_at',
                'updated_at'
            ]
        )

        messages.success(
            request,
            'Assignment submitted successfully.'
        )

        return redirect('assignment_list')

    return redirect('assignment_list')

# ============================================================
# TEACHER REVIEW SUBMISSION
# ============================================================

def review_assignment(request, assignment_id):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.is_staff:
        return redirect('dashboard')

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        assigned_by=request.user
    )

    if assignment.submission_status == 'Submitted':
        assignment.submission_status = 'Reviewed'
        assignment.save(
            update_fields=[
                'submission_status',
                'updated_at'
            ]
        )

        messages.success(
            request,
            'Student submission marked as reviewed.'
        )

    return redirect(
        'teacher_student_detail',
        assignment.user.id
    )


