

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils.dateparse import parse_date
from django.db.models import Q

from auth_system.permissions.token_valid import IsTokenValid
from lead.models.enquiry import Enquiry
from lead.serializers.enquiry_serializer import EnquirySerializer
from auth_system.utils.pagination import CustomPagination
from django.http import HttpResponse
import pandas as pd

class EnquiryReportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request):
        data = request.data

        to_date = data.get("to_date")
        from_date = data.get("from_date")
        employee_id = data.get("employee_id")
        assign_to = data.get("assign_to")
        status_val = data.get("status")

        filters = Q()

        # Date validation
        if from_date and not to_date:
            return Response({
                "success": False,
                "message": "Please select 'to_date' when using 'from_date'."
            }, status=status.HTTP_400_BAD_REQUEST)

        if to_date:
            to_date = parse_date(to_date)
            if not to_date:
                return Response({"success": False, "message": "Invalid 'to_date' format. Use YYYY-MM-DD."},
                                status=status.HTTP_400_BAD_REQUEST)

            if from_date:
                from_date = parse_date(from_date)
                if not from_date:
                    return Response({"success": False, "message": "Invalid 'from_date' format. Use YYYY-MM-DD."},
                                    status=status.HTTP_400_BAD_REQUEST)
                filters &= Q(created_at__date__range=[from_date, to_date])
            else:
                filters &= Q(created_at__date=to_date)

        if employee_id:
            filters &= Q(created_by=employee_id)

        if assign_to:
            filters &= Q(assign_to=assign_to)

        if status_val is not None:
            filters &= Q(is_status=status_val)

        enquiries = Enquiry.objects.filter(filters).order_by("id")

        # paginator = CustomPagination()
        # page_data = paginator.paginate_queryset(enquiries, request)
        # serializer = EnquirySerializer(page_data, many=True)
        serializer = EnquirySerializer(enquiries, many=True)

        # return paginator.get_custom_paginated_response(
        #     data=serializer.data,
        #     extra_fields={
        #         "success": True,
        #         "message": "Enquiries report retrieved successfully (paginated).",
        #     }
        # )

        return Response({
            "success": True,
            "message": "Enquiries report retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)



class EnquiryReportDownloadAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request):
        data = request.data
        to_date = data.get("to_date")
        from_date = data.get("from_date")
        employee_id = data.get("employee_id")
        assign_to = data.get("assign_to")
        status_val = data.get("status")

        filters = Q()
        if from_date and not to_date:
            return Response({"success": False, "message": "Please select 'to_date' when using 'from_date'."}, status=400)

        if to_date:
            to_date = parse_date(to_date)
            if from_date:
                from_date = parse_date(from_date)
                filters &= Q(created_at__date__range=[from_date, to_date])
            else:
                filters &= Q(created_at__date=to_date)

        if employee_id:
            filters &= Q(created_by=employee_id)
        if assign_to:
            filters &= Q(assign_to=assign_to)
        if status_val is not None:
            filters &= Q(is_status=status_val)

        enquiries = Enquiry.objects.filter(filters).order_by("id")
        serializer = EnquirySerializer(enquiries, many=True)

        cleaned_data = []
        for enquiry in serializer.data:
            row = {
                "ID": enquiry.get("id"),
                "Name": enquiry.get("name"),
                "Mobile Number": enquiry.get("mobile_number"),
                "LAN Number": enquiry.get("lan_number"),
                "Occupation": enquiry.get("occupation_display"),
                "Employer": enquiry.get("employer_name"),
                "Monthly Income": enquiry.get("monthly_income"),
                "KYC Document": enquiry.get("kyc_document"),
                "KYC Number": enquiry.get("kyc_number"),
                "Status": enquiry.get("is_status_display"),
                "Steps": enquiry.get("is_steps_display"),
            }

            if enquiry.get("enquiry_loan_details"):
                loan = enquiry["enquiry_loan_details"][0]
                row.update({
                    "Loan Type": loan.get("loan_type_display"),
                    "Loan Amount Range": loan.get("loan_amount_range_display"),
                    "Property Type": loan.get("property_type_display"),
                    "Property Document": loan.get("property_document_type_display"),
                    "Loan Required On": loan.get("loan_required_on_display"),
                    "Enquiry Type": loan.get("enquiry_type_display"),
                    "Property Value": loan.get("property_value"),
                    "Remark": loan.get("remark"),
                })

            if enquiry.get("enquiry_verification"):
                ver = enquiry["enquiry_verification"]
                row.update({
                    "Mobile": ver.get("mobile"),
                    "Mobile Status": ver.get("mobile_status_display"),
                    "Email": ver.get("email"),
                    "Email Status": ver.get("email_status_display"),
                    "Aadhaar Verified": ver.get("aadhaar_verified"),
                })

            cleaned_data.append(row)

        df = pd.DataFrame(cleaned_data)

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="enquiries_report.xlsx"'
        df.to_excel(response, index=False)
        return response