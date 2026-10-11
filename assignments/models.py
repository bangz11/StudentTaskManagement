from django.db import models
from django.contrib.auth.models import User


class Assignment(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    SUBMISSION_STATUS_CHOICES = [
        ('Not Submitted', 'Not Submitted'),
        ('Submitted', 'Submitted'),
        ('Reviewed', 'Reviewed'),
    ]

    # Student who receives the assignment
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assignments'
    )

    # Teacher who created/assigned the assignment
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_work'
    )

    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Teacher's assignment/instruction file
    assignment_file = models.FileField(
        upload_to='assignments/',
        blank=True,
        null=True
    )

    file_text = models.TextField(
        blank=True,
        null=True
    )

    due_date = models.DateField()

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='Medium'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    # Student's completed work
    submission_file = models.FileField(
        upload_to='submissions/',
        blank=True,
        null=True
    )

    submission_status = models.CharField(
        max_length=20,
        choices=SUBMISSION_STATUS_CHOICES,
        default='Not Submitted'
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title