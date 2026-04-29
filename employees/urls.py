from django.urls import path

from employees.views import EmployeeRecordListCreateAPIView, EmployeeSalaryDetailsAPIView

urlpatterns = [
    path("employees/", EmployeeRecordListCreateAPIView.as_view(), name="employee-list-create"),
    path(
        "employees//salary-details/",
        EmployeeSalaryDetailsAPIView.as_view(),
        {"employee_id": ""},
    ),
    path(
        "employees/<employee_id>/salary-details/",
        EmployeeSalaryDetailsAPIView.as_view(),
        name="employee-salary-details",
    ),
]
