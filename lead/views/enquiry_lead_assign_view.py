from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from lead.models.enquiry import Enquiry
from lead.models.lead_logs import LeadLog  
from auth_system.permissions.token_valid import IsTokenValid
from django.shortcuts import get_object_or_404
from django.utils import timezone
from lead.models.enquiry_lead_assign_log import LeadAssignLog
from ems.models.emp_basic_profile import TblEmpBasicProfile
from auth_system.models.user import TblUser  
from django.db import transaction
from ems.models.branch import TblBranch
from ems.serializers.branch_serializers import TblBranchSerializer

from lead.serializers.employee_serializers import EmployeeSerializer 
from lead.serializers.enquiry_serializer import EnquirySerializer

class GetBranchAndFilterEmployeesAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        try:
            branch_id = request.query_params.get("branch_id")
            branches = []
            employees = []

            if branch_id:
                branch = TblBranch.objects.filter(id=branch_id, deleted_at__isnull=True).first()
                if branch:
                    branches = TblBranchSerializer(branch).data if branch else []
                
                employees_query = TblUser.objects.filter(branch_id=branch_id, is_active=True)
                employees = EmployeeSerializer(employees_query, many=True).data
            else:
                all_branches = TblBranch.objects.filter(deleted_at__isnull=True)
                branches = TblBranchSerializer(all_branches, many=True).data

            return Response(
                {"branches": branches, "employees": employees},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": "Something went wrong.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LeadAssignView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request, enquiry_id):
        data = request.data
        employee_id = data.get("employee_id")
        remark = data.get("remark")
        branch_id = data.get("branch_id")

        if not employee_id:
            return Response(
                {"success": False, "message": "Select Employee."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not remark:
            return Response(
                {"success": False, "message": "Remark is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not branch_id:
            return Response(
                {"success": False, "message": "Branch is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        enquiry = get_object_or_404(Enquiry, id=enquiry_id)

        user = get_object_or_404(TblUser, id=employee_id)

        employee_profile = get_object_or_404(
            TblEmpBasicProfile, employee_code=user.employee_code
        )

        branch = get_object_or_404(TblBranch, id=branch_id)

        with transaction.atomic():
            LeadAssignLog.objects.create(
                enquiry=enquiry,
                employee=employee_profile,  
                branch=branch,
                remark=remark,
                created_by=request.user.id
            )

            LeadLog.objects.create(
                enquiry=enquiry,
                status=f"Lead assigned to employee {user.full_name} in branch {branch.branch_name}",
                created_by=request.user.id,
                remark=remark
            )

            enquiry.assign_to = employee_profile 
            enquiry.branch = branch
            enquiry.updated_at = timezone.now()
            enquiry.updated_by = request.user.id
            enquiry.save()

            LeadLog.objects.create(
                enquiry=enquiry,
                status="assign_to updated",
                created_by=request.user.id,
                remark="Updated enquiry's assign_to field due to lead assignment"
            )

        return Response(
            {"success": True, "message": "Assigned successfully."},
            status=status.HTTP_200_OK
        )


class GetAssigned(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        userId = request.user.id  

        enquiries = Enquiry.objects.filter(assign_to_id=userId)

        if not enquiries.exists():
            return Response(
                {"message": "No enquiries assigned to you."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EnquirySerializer(enquiries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)