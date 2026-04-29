from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.core_logic import EmployeeTaxDeductionCalculator
from employees.models import EmployeeRecord
from employees.serializers import EmployeeSerializer


class EmployeeRecordListCreateAPIView(APIView):
    def get(self, request):
        employees = EmployeeRecord.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EmployeeSalaryDetailsAPIView(APIView):
    @staticmethod
    def _parse_employee_id(employee_id: str) -> int:
        normalized_employee_id = str(employee_id).strip()

        if not normalized_employee_id:
            raise NotFound("Employee not found.")
        if not normalized_employee_id.isdigit():
            raise NotFound("Employee not found.")

        parsed_employee_id = int(normalized_employee_id)
        if parsed_employee_id <= 0:
            raise NotFound("Employee not found.")

        return parsed_employee_id

    def get(self, request, employee_id: str):
        parsed_employee_id = self._parse_employee_id(employee_id)
        employee = get_object_or_404(EmployeeRecord, id=parsed_employee_id)
        salary_details = EmployeeTaxDeductionCalculator.build_salary_details(
            employee.salary,
            employee.country,
        )
        return Response(
            {
                "id": employee.id,
                "full_name": employee.full_name,
                "country": employee.country,
                **salary_details,
            },
            status=status.HTTP_200_OK,
        )
