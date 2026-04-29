from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from employees.models import EmployeeRecord


class CountrySalaryMetricsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def _url(self, country: str) -> str:
        return f"/api/metrics/country/{country}/"

    def test_country_metrics_returns_min_max_and_average_salary(self):
        EmployeeRecord.objects.create(
            full_name="Aarav Singh",
            job_title="Engineer",
            country="India",
            salary=Decimal("1000.10"),
        )
        EmployeeRecord.objects.create(
            full_name="Neha Patel",
            job_title="Engineer",
            country="India",
            salary=Decimal("1000.20"),
        )
        EmployeeRecord.objects.create(
            full_name="Liam Scott",
            job_title="Engineer",
            country="United States",
            salary=Decimal("5000.00"),
        )

        response = self.client.get(self._url("India"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(str(response.data["min_salary"])), Decimal("1000.10"))
        self.assertEqual(Decimal(str(response.data["max_salary"])), Decimal("1000.20"))
        self.assertEqual(Decimal(str(response.data["avg_salary"])), Decimal("1000.15"))

    def test_country_metrics_treats_india_case_insensitively_for_ten_percent_rule(self):
        EmployeeRecord.objects.create(
            full_name="Meera Nair",
            job_title="QA Engineer",
            country="India",
            salary=Decimal("1000.00"),
        )
        EmployeeRecord.objects.create(
            full_name="Rohan Iyer",
            job_title="QA Engineer",
            country="India",
            salary=Decimal("2000.00"),
        )

        response = self.client.get(self._url("india"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(str(response.data["country_tax_rate"])), Decimal("0.10"))
        self.assertEqual(
            Decimal(str(response.data["avg_salary_after_tax"])),
            Decimal("1350.00"),
        )

    def test_country_metrics_returns_not_found_when_country_has_no_employees(self):
        response = self.client.get(self._url("India"))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("not found", response.content.decode().lower())

    def test_country_metrics_uses_decimal_precision_without_float_rounding_errors(self):
        EmployeeRecord.objects.create(
            full_name="Nina Dsouza",
            job_title="Analyst",
            country="India",
            salary=Decimal("10.10"),
        )
        EmployeeRecord.objects.create(
            full_name="Rahul Das",
            job_title="Analyst",
            country="India",
            salary=Decimal("10.20"),
        )
        EmployeeRecord.objects.create(
            full_name="Kiran Rao",
            job_title="Analyst",
            country="India",
            salary=Decimal("10.30"),
        )

        response = self.client.get(self._url("India"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(str(response.data["avg_salary"])), Decimal("10.20"))


class JobTitleSalaryMetricsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def _url(self, title: str) -> str:
        return f"/api/metrics/job-title/{title}/"

    def test_job_title_metrics_returns_average_salary_for_specific_title(self):
        EmployeeRecord.objects.create(
            full_name="Asha Verma",
            job_title="Data Scientist",
            country="India",
            salary=Decimal("3000.00"),
        )
        EmployeeRecord.objects.create(
            full_name="Ben White",
            job_title="Data Scientist",
            country="United States",
            salary=Decimal("5000.00"),
        )
        EmployeeRecord.objects.create(
            full_name="Chris Brown",
            job_title="Designer",
            country="India",
            salary=Decimal("7000.00"),
        )

        response = self.client.get(self._url("Data Scientist"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["job_title"], "Data Scientist")
        self.assertEqual(Decimal(str(response.data["avg_salary"])), Decimal("4000.00"))

    def test_job_title_metrics_returns_not_found_when_title_has_no_employees(self):
        response = self.client.get(self._url("DevOps Engineer"))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("not found", response.content.decode().lower())

    def test_job_title_metrics_uses_decimal_precision_for_average_salary(self):
        EmployeeRecord.objects.create(
            full_name="Diya Sen",
            job_title="Backend Engineer",
            country="India",
            salary=Decimal("0.10"),
        )
        EmployeeRecord.objects.create(
            full_name="Ethan Cruz",
            job_title="Backend Engineer",
            country="United States",
            salary=Decimal("0.20"),
        )
        EmployeeRecord.objects.create(
            full_name="Farah Ali",
            job_title="Backend Engineer",
            country="India",
            salary=Decimal("0.30"),
        )

        response = self.client.get(self._url("Backend Engineer"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(str(response.data["avg_salary"])), Decimal("0.20"))