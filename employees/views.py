from decimal import Decimal, ROUND_HALF_UP

import logging

from django.db.models import Count, Max, Min, Sum
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import APIException, NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.config import EMPLOYEE_TAX_RATES
from employees.core_logic import EmployeeTaxDeductionCalculator, TWOPLACES
from employees.models import EmployeeRecord
from employees.serializers import EmployeeSerializer

logger = logging.getLogger(__name__)


class EmployeeRecordListCreateAPIView(APIView):
    def get(self, request):
        try:
            employees = EmployeeRecord.objects.all()
            serializer = EmployeeSerializer(employees, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except APIException:
            logger.info("API error listing employees.", exc_info=True)
            raise
        except Exception:
            logger.exception("Unhandled error listing employees.")
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        try:
            serializer = EmployeeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except APIException:
            logger.info("API error creating employee record.", exc_info=True)
            raise
        except Exception:
            logger.exception("Unhandled error creating employee record.")
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EmployeeSalaryDetailsAPIView(APIView):
    @staticmethod
    def _parse_employee_id(employee_id: str) -> int:
        try:
            normalized_employee_id = str(employee_id).strip()

            if not normalized_employee_id:
                raise NotFound("Employee not found.")
            if not normalized_employee_id.isdigit():
                raise NotFound("Employee not found.")

            parsed_employee_id = int(normalized_employee_id)
            if parsed_employee_id <= 0:
                raise NotFound("Employee not found.")

            return parsed_employee_id
        except NotFound:
            logger.warning("Employee not found: invalid employee_id=%r", employee_id, exc_info=True)
            raise
        except Exception:
            logger.exception("Unhandled error parsing employee_id=%r", employee_id)
            raise

    def get(self, request, employee_id: str):
        try:
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
        except NotFound:
            logger.warning("Salary details not found for employee_id=%r", employee_id, exc_info=True)
            raise
        except APIException:
            logger.info("API error fetching salary details for employee_id=%r", employee_id, exc_info=True)
            raise
        except Exception:
            logger.exception("Unhandled error fetching salary details for employee_id=%r", employee_id)
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CountrySalaryMetricsAPIView(APIView):
    @staticmethod
    def _resolve_country_tax_key(country: str) -> str | None:
        try:
            normalized = (country or "").strip()
            for tax_country in EMPLOYEE_TAX_RATES.keys():
                if tax_country.lower() == normalized.lower():
                    return tax_country
            return None
        except Exception:
            logger.exception("Unhandled error resolving country tax key for country=%r", country)
            raise

    @staticmethod
    def _avg_from_total_and_count(total: Decimal, count: int) -> Decimal:
        try:
            # Ensure we never divide using floats; keep money in Decimal.
            return (total / Decimal(count)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
        except Exception:
            logger.exception("Unhandled error computing avg salary from total=%r count=%r", total, count)
            raise

    def get(self, request, country: str):
        try:
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
            avg_salary = self._avg_from_total_and_count(agg["total_salary"] or Decimal("0"), int(agg["count"]))

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
        except NotFound:
            logger.warning("Country salary metrics not found for country=%r", country, exc_info=True)
            raise
        except APIException:
            logger.info("API error fetching country salary metrics for country=%r", country, exc_info=True)
            raise
        except Exception:
            logger.exception("Unhandled error fetching country salary metrics for country=%r", country)
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class JobTitleSalaryMetricsAPIView(APIView):
    @staticmethod
    def _avg_from_total_and_count(total: Decimal, count: int) -> Decimal:
        try:
            return (total / Decimal(count)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
        except Exception:
            logger.exception("Unhandled error computing avg salary from total=%r count=%r", total, count)
            raise

    def get(self, request, title: str):
        try:
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
        except NotFound:
            logger.warning("Job title salary metrics not found for title=%r", title, exc_info=True)
            raise
        except APIException:
            logger.info("API error fetching job title salary metrics for title=%r", title, exc_info=True)
            raise
        except Exception:
            logger.exception("Unhandled error fetching job title salary metrics for title=%r", title)
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
