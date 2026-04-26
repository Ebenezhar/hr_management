from django.urls import path

from employees.views import EmployeeRecordListCreateAPIView

urlpatterns = [
    path("employees/", EmployeeRecordListCreateAPIView.as_view(), name="employee-list-create"),
]
