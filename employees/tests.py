from django.test import TestCase
from employees.models import Employee

class EmployeeModelTest(TestCase):
    def test_create_employee(self):
        employee = EmployeeRecord.objects.create(
            full_name="Ebenezhar Balu",
            job_title="Senior Developer",
            country="India",
            salary=100000
        )
        self.assertEqual(employee.full_name, "Ebenezhar Balu")