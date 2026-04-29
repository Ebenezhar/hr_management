from django.urls import path

from employees.views import (
    CountrySalaryMetricsAPIView,
    EmployeeRecordListCreateAPIView,
    EmployeeSalaryDetailsAPIView,
    JobTitleSalaryMetricsAPIView,
)

urlpatterns = [
    path("employees/", EmployeeRecordListCreateAPIView.as_view(), name="employee-list-create"),
    path("employees//salary-details/", EmployeeSalaryDetailsAPIView.as_view(),{"employee_id": ""}),
    path("employees/<employee_id>/salary-details/", EmployeeSalaryDetailsAPIView.as_view(), name="employee-salary-details"),
    path("employees/metrics/country/<str:country>/", CountrySalaryMetricsAPIView.as_view(), name="country-salary-metrics"),
    path("employees/metrics/job-title/<str:title>/", JobTitleSalaryMetricsAPIView.as_view(), name="job-title-salary-metrics"),
]
 