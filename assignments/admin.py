from django.contrib import admin
from .models import Assignment


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'subject',
        'due_date',
        'priority',
        'status',
        'user',
    )

    list_filter = (
        'priority',
        'status',
        'subject',
    )

    search_fields = (
        'title',
        'subject',
        'description',
    )