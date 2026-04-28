from decimal import Decimal, ROUND_HALF_UP


TAX_DEDUCTION_RATE = Decimal("0.10")
TWOPLACES = Decimal("0.01")


class EmployeeTaxDeductionCalculator:
    @staticmethod
    def calculate_tax_deduction(salary: Decimal) -> Decimal:
        return (salary * TAX_DEDUCTION_RATE).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    @classmethod
    def build_salary_details(cls, salary: Decimal) -> dict[str, Decimal]:
        tax_deduction = cls.calculate_tax_deduction(salary)
        net_salary = (salary - tax_deduction).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
        return {
            "salary": salary.quantize(TWOPLACES, rounding=ROUND_HALF_UP),
            "tax_deduction": tax_deduction,
            "net_salary": net_salary,
        }
