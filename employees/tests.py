from decimal import Decimal

from django.test import SimpleTestCase
from django.urls import reverse  # noqa: F401
from rest_framework import status
from rest_framework.test import APITestCase

from employees.models import EmployeeRecord
from employees.serializers import EmployeeSerializer


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


class EmployeeSerializerValidationTests(SimpleTestCase):
    def _valid_payload(self, **overrides):
        payload = {
            "full_name": "John Doe",
            "job_title": "Software Engineer",
            "country": "United Kingdom",
            "salary": "250000.00",
        }
        payload.update(overrides)
        return payload

    def test_valid_payload_is_valid(self):
        s = EmployeeSerializer(data=self._valid_payload())
        self.assertTrue(s.is_valid(), s.errors)

    def test_full_name_strips_and_collapses_whitespace(self):
        s = EmployeeSerializer(data=self._valid_payload(full_name="  John   Doe  "))
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data["full_name"], "John Doe")

    def test_full_name_rejects_empty_or_whitespace(self):
        s = EmployeeSerializer(data=self._valid_payload(full_name="   "))
        self.assertFalse(s.is_valid())
        self.assertIn("full_name", s.errors)

    def test_full_name_rejects_invalid_characters(self):
        s = EmployeeSerializer(data=self._valid_payload(full_name="John@Doe"))
        self.assertFalse(s.is_valid())
        self.assertIn("full_name", s.errors)

    def test_job_title_strips_and_collapses_whitespace(self):
        s = EmployeeSerializer(data=self._valid_payload(job_title="  Senior   Dev  "))
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data["job_title"], "Senior Dev")

    def test_job_title_rejects_empty_or_whitespace(self):
        s = EmployeeSerializer(data=self._valid_payload(job_title="  "))
        self.assertFalse(s.is_valid())
        self.assertIn("job_title", s.errors)

    def test_job_title_rejects_invalid_characters(self):
        s = EmployeeSerializer(data=self._valid_payload(job_title="Dev<>Ops"))
        self.assertFalse(s.is_valid())
        self.assertIn("job_title", s.errors)

    def test_country_strips_and_collapses_whitespace(self):
        s = EmployeeSerializer(data=self._valid_payload(country="  United   States  "))
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data["country"], "United States")

    def test_country_rejects_empty_or_whitespace(self):
        s = EmployeeSerializer(data=self._valid_payload(country="   "))
        self.assertFalse(s.is_valid())
        self.assertIn("country", s.errors)

    def test_country_rejects_invalid_characters(self):
        s = EmployeeSerializer(data=self._valid_payload(country="Ind1a"))
        self.assertFalse(s.is_valid())
        self.assertIn("country", s.errors)

    def test_salary_accepts_decimal_and_string(self):
        s1 = EmployeeSerializer(data=self._valid_payload(salary="1234.50"))
        self.assertTrue(s1.is_valid(), s1.errors)
        self.assertEqual(s1.validated_data["salary"], Decimal("1234.50"))

        s2 = EmployeeSerializer(data=self._valid_payload(salary=Decimal("999.99")))
        self.assertTrue(s2.is_valid(), s2.errors)
        self.assertEqual(s2.validated_data["salary"], Decimal("999.99"))

    def test_salary_rejects_non_numeric(self):
        s = EmployeeSerializer(data=self._valid_payload(salary="abc"))
        self.assertFalse(s.is_valid())
        self.assertIn("salary", s.errors)

    def test_salary_rejects_zero_or_negative(self):
        s1 = EmployeeSerializer(data=self._valid_payload(salary="0"))
        self.assertFalse(s1.is_valid())
        self.assertIn("salary", s1.errors)

        s2 = EmployeeSerializer(data=self._valid_payload(salary="-1"))
        self.assertFalse(s2.is_valid())
        self.assertIn("salary", s2.errors)

    def test_salary_rejects_too_large(self):
        s = EmployeeSerializer(data=self._valid_payload(salary="10000000000.00"))
        self.assertFalse(s.is_valid())
        self.assertIn("salary", s.errors)