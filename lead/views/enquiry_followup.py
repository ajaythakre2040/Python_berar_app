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

class EnquiryFollowUpCountAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        today = date.today()

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
        active_enquiries = Enquiry.objects.filter(
            is_status=EnquiryStatus.ACTIVE,
            deleted_at__isnull=True
        ).order_by("-id")

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
        closed_enquiries = Enquiry.objects.filter(
            is_status=EnquiryStatus.CLOSED,
            deleted_at__isnull=True
        ).order_by("-id")

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
    