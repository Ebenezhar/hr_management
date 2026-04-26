from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

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
