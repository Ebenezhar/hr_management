from rest_framework import serializers

from decimal import Decimal, InvalidOperation
import re

from employees.models import EmployeeRecord
from employees.config import ACCEPTED_COUNTRIES


class EmployeeSerializer(serializers.ModelSerializer):
    _FULL_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z .'\-]*[A-Za-z.]$")
    _JOB_TITLE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 &/().,'\-]*[A-Za-z0-9)]$")
    _COUNTRY_RE = re.compile(r"^[A-Za-z][A-Za-z '\-]*[A-Za-z]$")

    class Meta:
        model = EmployeeRecord
        fields = ["id", "full_name", "job_title", "country", "salary"]

    def validate_full_name(self, value: str) -> str:
        value = " ".join((value or "").split())
        if not value:
            raise serializers.ValidationError("Full name is required.")
        if len(value) < 2 or len(value) > 255:
            raise serializers.ValidationError("Full name must be between 2 and 255 characters.")
        if not self._FULL_NAME_RE.match(value):
            raise serializers.ValidationError(
                "Full name may contain only letters, spaces, apostrophes ('), hyphens (-), and dots (.)."
            )
        return value

    def validate_job_title(self, value: str) -> str:
        value = " ".join((value or "").split())
        if not value:
            raise serializers.ValidationError("Job title is required.")
        if len(value) < 2 or len(value) > 255:
            raise serializers.ValidationError("Job title must be between 2 and 255 characters.")
        if not self._JOB_TITLE_RE.match(value):
            raise serializers.ValidationError("Job title contains invalid characters.")
        return value

    def validate_country(self, value: str) -> str:
        value = " ".join((value or "").split())
        if not value:
            raise serializers.ValidationError("Country is required.")
        if len(value) < 2 or len(value) > 100:
            raise serializers.ValidationError("Country must be between 2 and 100 characters.")
        if not self._COUNTRY_RE.match(value):
            raise serializers.ValidationError(
                "Country may contain only letters, spaces, apostrophes ('), and hyphens (-)."
            )
        if value not in ACCEPTED_COUNTRIES:
            raise serializers.ValidationError("Country must be one of the accepted choices.")
        return value

    def validate_salary(self, value):
        try:
            salary = value if isinstance(value, Decimal) else Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            raise serializers.ValidationError("Salary must be a valid number.")

        if salary <= 0:
            raise serializers.ValidationError("Salary must be greater than 0.")

        if salary > Decimal("9999999999.99"):
            raise serializers.ValidationError("Salary is too large.")

        return salary
