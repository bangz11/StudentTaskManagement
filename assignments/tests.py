from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Assignment


class AssignmentTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='student1',
            password='testpass123'
        )

        self.other_user = User.objects.create_user(
            username='student2',
            password='testpass123'
        )

        self.assignment = Assignment.objects.create(
            user=self.user,
            title='Database Assignment',
            subject='Database',
            description='Complete database work',
            due_date=date(2026, 10, 10),
            priority='High',
            status='Pending'
        )

    def test_user_login(self):
        response = self.client.post(
            '/login/',
            {
                'username': 'student1',
                'password': 'testpass123'
            }
        )

        self.assertEqual(response.status_code, 302)

    def test_assignment_belongs_to_user(self):
        self.assertEqual(self.assignment.user, self.user)

    def test_user_can_view_own_assignments(self):
        self.client.login(
            username='student1',
            password='testpass123'
        )

        response = self.client.get('/assignments/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Database Assignment')

    def test_user_can_create_assignment(self):
        self.client.login(
            username='student1',
            password='testpass123'
        )

        response = self.client.post(
            '/assignments/add/',
            {
                'title': 'Web Development',
                'subject': 'Web Development',
                'description': 'Build a website',
                'due_date': '2026-10-20',
                'priority': 'Medium',
                'status': 'Pending'
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Assignment.objects.filter(
                title='Web Development',
                user=self.user
            ).exists()
        )

    def test_user_cannot_edit_other_users_assignment(self):
        self.client.login(
            username='student2',
            password='testpass123'
        )

        response = self.client.get(
            f'/assignments/{self.assignment.id}/edit/'
        )

        self.assertEqual(response.status_code, 404)


class AssignmentAPITests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser',
            password='testpass123'
        )

        self.other_user = User.objects.create_user(
            username='otherapiuser',
            password='testpass123'
        )

        self.client = APIClient()

        self.assignment = Assignment.objects.create(
            user=self.user,
            title='API Assignment',
            subject='Programming',
            description='API test assignment',
            due_date=date(2026, 10, 15),
            priority='Medium',
            status='Pending'
        )

    def test_api_requires_login(self):
        response = self.client.get('/api/assignments/')

        self.assertIn(response.status_code, [401, 403])

    def test_authenticated_user_can_list_assignments(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/assignments/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_authenticated_user_can_create_assignment(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/api/assignments/',
            {
                'title': 'New API Assignment',
                'subject': 'Python',
                'description': 'Created through API',
                'due_date': '2026-10-25',
                'priority': 'High',
                'status': 'Pending'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Assignment.objects.filter(
                title='New API Assignment',
                user=self.user
            ).exists()
        )

    def test_user_cannot_access_other_users_assignment(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(
            f'/api/assignments/{self.assignment.id}/'
        )

        self.assertEqual(response.status_code, 404)



class TeacherPortalTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.teacher = User.objects.create_user(
            username='teacher_test',
            password='TeacherPass123!'
        )
        self.teacher.is_staff = True
        self.teacher.save()

        self.student = User.objects.create_user(
            username='student_test',
            password='StudentPass123!'
        )

        Assignment.objects.create(
            user=self.student,
            title='Test Assignment',
            subject='Information Technology',
            description='Teacher test assignment',
            due_date=date.today(),
            priority='High',
            status='Pending'
        )

    def test_teacher_can_access_dashboard(self):
        self.client.login(
            username='teacher_test',
            password='TeacherPass123!'
        )

        response = self.client.get('/teacher/dashboard/')

        self.assertEqual(response.status_code, 200)

    def test_teacher_can_view_students(self):
        self.client.login(
            username='teacher_test',
            password='TeacherPass123!'
        )

        response = self.client.get('/teacher/students/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'student_test')

    def test_teacher_can_view_student_assignments(self):
        self.client.login(
            username='teacher_test',
            password='TeacherPass123!'
        )

        response = self.client.get(
            f'/teacher/students/{self.student.id}/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Assignment')

    def test_student_cannot_access_teacher_dashboard(self):
        self.client.login(
            username='student_test',
            password='StudentPass123!'
        )

        response = self.client.get('/teacher/dashboard/')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
