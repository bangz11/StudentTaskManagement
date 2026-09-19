from rest_framework import serializers
from .models import Assignment

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = [
            'id',
            'user',
            'title',
            'subject',
            'description',
            'due_date',
            'priority',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at']
