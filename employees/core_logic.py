from decimal import Decimal, ROUND_HALF_UP

from employees.config import EMPLOYEE_TAX_RATES


TWOPLACES = Decimal("0.01")


class EmployeeTaxDeductionCalculator:
    @staticmethod
    def get_tax_rate(country: str) -> Decimal:
        return EMPLOYEE_TAX_RATES.get(country, Decimal("0.00"))

    @classmethod
    def calculate_tax_deduction(cls, salary: Decimal, country: str) -> Decimal:
        tax_rate = cls.get_tax_rate(country)
        return (salary * tax_rate).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    @classmethod
    def build_salary_details(cls, salary: Decimal, country: str) -> dict[str, Decimal]:
        tax_rate = cls.get_tax_rate(country)
        tax_deduction = cls.calculate_tax_deduction(salary, country)
        net_salary = (salary - tax_deduction).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
        return {
            "salary": salary.quantize(TWOPLACES, rounding=ROUND_HALF_UP),
            "tax_rate": tax_rate.quantize(TWOPLACES, rounding=ROUND_HALF_UP),
            "tax_deduction": tax_deduction,
            "net_salary": net_salary,
        }
