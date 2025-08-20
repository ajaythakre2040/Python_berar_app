# lead/views/enquiry_followup.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from datetime import date

from lead.models.enquiry_loan_details import EnquiryLoanDetails
from lead.models.enquiry import Enquiry
from lead.models.lead_logs import LeadLog  # import LeadLog model
from lead.serializers.enquiry_serializer import EnquirySerializer
from auth_system.permissions.token_valid import IsTokenValid
from auth_system.utils.pagination import CustomPagination
from constants import EnquiryStatus
from django.shortcuts import get_object_or_404
from django.utils import timezone
from lead.models.enquiry_lead_assign_log import LeadAssignLog
from ems.models.emp_basic_profile import TblEmpBasicProfile
from django.db import transaction

class EnquiryFollowUpCountAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        today = date.today()
        count_only = request.query_params.get("count_only") == "true"

        loan_qs = EnquiryLoanDetails.objects.filter(
            followup_pickup_date__gte=today,
            enquiry__deleted_at__isnull=True
        )

        enquiry_ids = loan_qs.values_list('enquiry_id', flat=True).distinct()

        enquiries = Enquiry.objects.filter(id__in=enquiry_ids)

        for loan_detail in loan_qs:
            LeadLog.objects.get_or_create(
                enquiry_id=loan_detail.enquiry_id,
                status="Follow-up Scheduled",
                defaults={
                    "created_by": 0,  
                    "remark": f"Follow-up scheduled for {loan_detail.followup_pickup_date}"
                }
            )

        total_count = enquiries.count()

        if count_only:
            return Response({
                "success": True,
                "message": "Total follow-up enquiry count retrieved.",
                "total_count": total_count
            }, status=status.HTTP_200_OK)
        
        paginator = CustomPagination()
        paginated_enquiries = paginator.paginate_queryset(enquiries, request)

        serializer = EnquirySerializer(paginated_enquiries, many=True)

        return paginator.get_paginated_response({
            "success": True,
            "message": "Enquiries with upcoming follow-up dates retrieved successfully.",
            "data": serializer.data
        })
    

class FollowUpUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request, *args, **kwargs):
        enquiry_id = request.data.get("enquiry_id")
        next_date = request.data.get("next_followup_date")
        status_value = request.data.get("status") 
        remark = request.data.get("remark")

        if not all([enquiry_id, next_date, status_value]):
            return Response({
                "success": False,
                "message": "Missing required fields."
            }, status=status.HTTP_400_BAD_REQUEST)

        if status_value.lower() == "active":
            new_status = EnquiryStatus.ACTIVE
        elif status_value.lower() == "closed":
            new_status = EnquiryStatus.CLOSED
        else:
            return Response({
                "success": False,
                "message": "Invalid status value. Must be 'active' or 'closed'."
            }, status=status.HTTP_400_BAD_REQUEST)

        enquiry = get_object_or_404(Enquiry, id=enquiry_id)
        loan_detail, _ = EnquiryLoanDetails.objects.get_or_create(enquiry=enquiry)

        loan_detail.followup_pickup_date = next_date
        loan_detail.save()

        enquiry.is_status = new_status
        enquiry.updated_at =  timezone.now()
        enquiry.updated_by =   request.user.id
        enquiry.save()

        LeadLog.objects.create(
            enquiry=enquiry,
            status="Follow-up Updated",
            created_by=request.user.id,
            remark=f"Status: {status_value.capitalize()} | Date: {next_date} | Remark: {remark}",
            followup_pickup_date=next_date,
        )

        return Response({
            "success": True,
            "message": "Follow-up updated successfully."
        }, status=status.HTTP_200_OK)


class ActiveEnquiriesAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]
  

    def get(self, request):
        count_only = request.query_params.get("count_only") == "true"

        active_enquiries = Enquiry.objects.filter(
            is_status=EnquiryStatus.ACTIVE,
            deleted_at__isnull=True
        ).order_by("-id")

        total_count = active_enquiries.count()

        if count_only:
            return Response({
                "success": True,
                "message": "Total active enquiry count retrieved.",
                "total_count": total_count
            }, status=status.HTTP_200_OK)

        paginator = CustomPagination()
        paginated_enquiries = paginator.paginate_queryset(active_enquiries, request)

        serializer = EnquirySerializer(paginated_enquiries, many=True)

        return paginator.get_paginated_response({
            "success": True,
            "message": "Active enquiries retrieved successfully.",
            "data": serializer.data
        })


class ClosedEnquiriesAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):

        count_only = request.query_params.get("count_only") == "true"

        closed_enquiries = Enquiry.objects.filter(
            is_status=EnquiryStatus.CLOSED,
            deleted_at__isnull=True
        ).order_by("-id")

        total_count = closed_enquiries.count()

        if count_only:
            return Response({
                "success": True,
                "message": "Total closed enquiry count retrieved.",
                "total_count": total_count
            }, status=status.HTTP_200_OK)
        

        paginator = CustomPagination()
        paginated_enquiries = paginator.paginate_queryset(closed_enquiries, request)

        serializer = EnquirySerializer(paginated_enquiries, many=True)

        return paginator.get_paginated_response({
            "success": True,
            "message": "Closed enquiries retrieved successfully.",
            "data": serializer.data
        })
    

class ReopenEnquiryView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request, enquiry_id):
        enquiry = get_object_or_404(Enquiry, id=enquiry_id)

        if enquiry.is_status != EnquiryStatus.CLOSED:
            return Response(
                {"success": False, "message": "Only CLOSED enquiries can be reopened."},
                status=status.HTTP_400_BAD_REQUEST
            )

        remark = request.data.get("remark")
        reopen = request.data.get("reopen", False)

        if reopen:
            enquiry.is_status = EnquiryStatus.ACTIVE 
            enquiry.updated_at =  timezone.now()
            enquiry.updated_by =   request.user.id
            enquiry.save()

            LeadLog.objects.create(
                enquiry=enquiry,
                status="RE OPEN",
                created_by=request.user.id,
                remark=remark
            )

            LeadLog.objects.create(
                enquiry=enquiry,
                status="ACTIVE",
                created_by=request.user.id,
                remark="Enquiry reopened and set to Active."
            )

            return Response(
                {"success": True, "message": "Enquiry reopened successfully."},
                status=status.HTTP_200_OK
            )

        return Response(
            {"success": False, "message": "Invalid input or 'reopen' not true."},
            status=status.HTTP_400_BAD_REQUEST
        )
    

class LeadAssignView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request, enquiry_id):
        data = request.data
        employee_id = data.get("employee_id")
        remark = data.get("remark")

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

        enquiry = get_object_or_404(Enquiry, id=enquiry_id)
        employee_profile = get_object_or_404(TblEmpBasicProfile, id=employee_id)

        with transaction.atomic():
            LeadAssignLog.objects.create(
                enquiry=enquiry,
                employee=employee_profile,  
                remark=remark,
                created_by=request.user.id 
            )

            LeadLog.objects.create(
                enquiry=enquiry,
                status="Lead assigned to employee.",
                created_by=request.user.id,
                remark=remark
            )

            enquiry.assign_to = employee_profile
            enquiry.updated_at = timezone.now()
            enquiry.updated_by = request.user.id
            enquiry.save()

            # Second LeadLog
            LeadLog.objects.create(
                enquiry=enquiry,
                status="assign_to updated-",
                created_by=request.user.id,
                remark='Updated enquiry s assign_to field due to lead assignment'
            )

        return Response(
            {"success": True, "message": "Assigned successfully."},
            status=status.HTTP_200_OK
        )


class AllCountAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        today = date.today()

        loan_qs = EnquiryLoanDetails.objects.filter(
            followup_pickup_date__gte=today,
            enquiry__deleted_at__isnull=True
        ).select_related("enquiry")

        enquiry_ids = loan_qs.values_list('enquiry_id', flat=True).distinct()
        followup_enquiries = Enquiry.objects.filter(id__in=enquiry_ids)

        for loan_detail in loan_qs:
            LeadLog.objects.get_or_create(
                enquiry_id=loan_detail.enquiry_id,
                status="Follow-up Scheduled",
                defaults={
                    "created_by": 0,
                    "remark": f"Follow-up scheduled for {loan_detail.followup_pickup_date}"
                }
            )

        total_enquiries_count = Enquiry.objects.filter(deleted_at__isnull=True).count()
        total_followup_count = followup_enquiries.count()
        total_active_count = Enquiry.objects.filter(
            is_status=EnquiryStatus.ACTIVE, deleted_at__isnull=True
        ).count()
        total_closed_count = Enquiry.objects.filter(
            is_status=EnquiryStatus.CLOSED, deleted_at__isnull=True
        ).count()

        return Response({
            "success": True,
            "message": "Enquiry counts retrieved successfully.",
            "total_enquiries_count": total_enquiries_count,
            "total_followup_count": total_followup_count,
            "total_active_count": total_active_count,
            "total_closed_count": total_closed_count
        }, status=status.HTTP_200_OK)
