from rest_framework import serializers

from employees.models import EmployeeRecord


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeRecord
        fields = ["id", "full_name", "job_title", "country", "salary"]
