from django.urls import path

from employees.views import EmployeeRecordListCreateAPIView, EmployeeSalaryDetailsAPIView

urlpatterns = [
    path("employees/", EmployeeRecordListCreateAPIView.as_view(), name="employee-list-create"),
    path(
        "employees/<int:employee_id>/salary-details/",
        EmployeeSalaryDetailsAPIView.as_view(),
        name="employee-salary-details",
    ),
]
