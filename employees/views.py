from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Count, Max, Min, Sum
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.config import EMPLOYEE_TAX_RATES
from employees.core_logic import EmployeeTaxDeductionCalculator, TWOPLACES
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


class CountrySalaryMetricsAPIView(APIView):
    @staticmethod
    def _resolve_country_tax_key(country: str) -> str | None:
        normalized = (country or "").strip()
        for tax_country in EMPLOYEE_TAX_RATES.keys():
            if tax_country.lower() == normalized.lower():
                return tax_country
        return None

    @staticmethod
    def _avg_from_total_and_count(total: Decimal, count: int) -> Decimal:
        # Ensure we never divide using floats; keep money in Decimal.
        return (total / Decimal(count)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    def get(self, request, country: str):
        resolved_country = (country or "").strip()

        qs = EmployeeRecord.objects.filter(country__iexact=resolved_country)
        agg = qs.aggregate(
            total_salary=Sum("salary"),
            count=Count("id"),
            min_salary=Min("salary"),
            max_salary=Max("salary"),
        )

        if not agg["count"]:
            raise NotFound("Not found.")

        min_salary = (agg["min_salary"] or Decimal("0")).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
        max_salary = (agg["max_salary"] or Decimal("0")).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
        avg_salary = self._avg_from_total_and_count(
            agg["total_salary"] or Decimal("0"),
            int(agg["count"]),
        )

        tax_key = self._resolve_country_tax_key(resolved_country)
        tax_rate = EmployeeTaxDeductionCalculator.get_tax_rate(tax_key) if tax_key else Decimal("0.00")
        tax_rate = tax_rate.quantize(TWOPLACES, rounding=ROUND_HALF_UP)

        # Apply tax to the computed average (not to each row) to keep the endpoint deterministic.
        tax_deduction = (avg_salary * tax_rate).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
        avg_salary_after_tax = (avg_salary - tax_deduction).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

        return Response(
            {
                "country": resolved_country,
                "min_salary": min_salary,
                "max_salary": max_salary,
                "avg_salary": avg_salary,
                "country_tax_rate": tax_rate,
                "avg_salary_after_tax": avg_salary_after_tax,
            },
            status=status.HTTP_200_OK,
        )


class JobTitleSalaryMetricsAPIView(APIView):
    @staticmethod
    def _avg_from_total_and_count(total: Decimal, count: int) -> Decimal:
        return (total / Decimal(count)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    def get(self, request, title: str):
        resolved_title = (title or "").strip()
        qs = EmployeeRecord.objects.filter(job_title__iexact=resolved_title)
        agg = qs.aggregate(
            total_salary=Sum("salary"),
            count=Count("id"),
        )

        if not agg["count"]:
            raise NotFound("Not found.")

        avg_salary = self._avg_from_total_and_count(
            agg["total_salary"] or Decimal("0"),
            int(agg["count"]),
        )

        return Response(
            {
                "job_title": resolved_title,
                "avg_salary": avg_salary,
            },
            status=status.HTTP_200_OK,
        )
