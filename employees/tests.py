from decimal import Decimal

from django.urls import reverse  # noqa: F401
from rest_framework import status
from rest_framework.test import APITestCase

from employees.models import EmployeeRecord


class EmployeeRecordListCreateApiTests(APITestCase):
    def test_list_employees_returns_existing_records(self):
        EmployeeRecord.objects.create(
            full_name="Ebenezhar Balu",
            job_title="Senior Developer",
            country="India",
            salary=Decimal("100000.00"),
        )

        response = self.client.get("/api/employees/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertIn("full_name", response.data[0])
        self.assertIn("job_title", response.data[0])
        self.assertIn("country", response.data[0])
        self.assertIn("salary", response.data[0])

    def test_create_employee_persists_and_returns_record(self):
        payload = {
            "full_name": "Adam",
            "job_title": "Engineer",
            "country": "UK",
            "salary": "250000.00",
        }

        response = self.client.post("/api/employees/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EmployeeRecord.objects.count(), 1)
        self.assertEqual(response.data["full_name"], payload["full_name"])
        self.assertEqual(response.data["job_title"], payload["job_title"])
        self.assertEqual(response.data["country"], payload["country"])
        self.assertIn("id", response.data)