from rest_framework.generics import ListCreateAPIView

from employees.models import EmployeeRecord
from employees.serializers import EmployeeSerializer


class EmployeeRecordListCreateAPIView(ListCreateAPIView):
    queryset = EmployeeRecord.objects.all()
    serializer_class = EmployeeSerializer
