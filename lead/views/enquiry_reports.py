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
from auth_system.models.user import TblUser  
from ems.models.branch import TblBranch
from datetime import date
from datetime import timedelta
from lead.models.enquiry_loan_details import EnquiryLoanDetails
# from ems.models.emp_basic_profile import TblEmpBasicProfile
from django.shortcuts import get_object_or_404

import pandas as pd



# class EnquiryReportAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsTokenValid]

#     def post(self, request):
#         data = request.data

#         to_date = data.get("to_date")
#         from_date = data.get("from_date")
#         employee_id = data.get("employee_id")
#         assign_to = data.get("assign_to")
#         status_val = data.get("status")

#         filters = Q()

#         if from_date and not to_date:
#             return Response(
#                 {
#                     "success": False,
#                     "message": "Please select 'to_date' when using 'from_date'.",
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         if to_date:
#             to_date = parse_date(to_date)
#             if not to_date:
#                 return Response(
#                     {
#                         "success": False,
#                         "message": "Invalid 'to_date' format. Use YYYY-MM-DD.",
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             if from_date:
#                 from_date = parse_date(from_date)
#                 if not from_date:
#                     return Response(
#                         {
#                             "success": False,
#                             "message": "Invalid 'from_date' format. Use YYYY-MM-DD.",
#                         },
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )
#                 filters &= Q(created_at__date__range=[from_date, to_date])
#             else:
#                 filters &= Q(created_at__date=to_date)

#         if employee_id:
#             filters &= Q(created_by=employee_id)

#         if assign_to:
#             filters &= Q(assign_to=assign_to)

#         if status_val is not None:
#             if status_val == 5:
#                 filters &= Q(is_status=0, created_at__date=date.today())
#             else:
#                 filters &= Q(is_status=status_val)

#         enquiries = Enquiry.objects.filter(filters).order_by("id")

#         paginator = CustomPagination()
#         page_data = paginator.paginate_queryset(enquiries, request)
#         serializer = EnquirySerializer(page_data, many=True)
#         # serializer = EnquirySerializer(enquiries, many=True)

#         return paginator.get_custom_paginated_response(
#             data=serializer.data,
#             extra_fields={
#                 "success": True,
#                 "message": "Enquiries report retrieved successfully (paginated).",
#             }
#         )

#         # return Response(
#         #     {
#         #         "success": True,
#         #         "message": "Enquiries report retrieved successfully.",
#         #         "data": serializer.data,
#         #     },
#         #     status=status.HTTP_200_OK,
#         # )

class EnquiryReportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request):
        data = request.data

        to_date = data.get("to_date")
        from_date = data.get("from_date")
        employee_id = data.get("employee_id")
        assign_to = data.get("assign_to")
        status_val = data.get("status")  # use this for follow-up logic

        filters = Q()

        # Date filters
        if from_date and not to_date:
            return Response(
                {"success": False, "message": "Please select 'to_date' when using 'from_date'."},
                status=400,
            )

        if to_date:
            to_date = parse_date(to_date)
            if not to_date:
                return Response(
                    {"success": False, "message": "Invalid 'to_date' format. Use YYYY-MM-DD."},
                    status=400,
                )

            if from_date:
                from_date = parse_date(from_date)
                if not from_date:
                    return Response(
                        {"success": False, "message": "Invalid 'from_date' format. Use YYYY-MM-DD."},
                        status=400,
                    )
                filters &= Q(created_at__date__range=[from_date, to_date])
            else:
                filters &= Q(created_at__date=to_date)

        # Other filters
        if employee_id:
            filters &= Q(created_by=employee_id)
        if assign_to:
            filters &= Q(assign_to=assign_to)

        # Status filter
        if status_val is not None:
            if int(status_val) == 5:
                # Status 5 = pending today
                filters &= Q(is_status=0, created_at__date=date.today())
            elif int(status_val) == 4:
                # Status 4 = follow-up scheduled today
                today = date.today()
                loan_qs = EnquiryLoanDetails.objects.filter(
                    followup_pickup_date=today
                )
                enquiry_ids = loan_qs.values_list("enquiry_id", flat=True).distinct()
                filters &= Q(id__in=enquiry_ids)
            else:
                filters &= Q(is_status=status_val)

        # Fetch enquiries
        enquiries = Enquiry.objects.filter(filters).order_by("id")

        # Pagination
        paginator = CustomPagination()
        page_data = paginator.paginate_queryset(enquiries, request)
        serializer = EnquirySerializer(page_data, many=True)

        return paginator.get_custom_paginated_response(
            data=serializer.data,
            extra_fields={
                "success": True,
                "message": "Enquiries report retrieved successfully (paginated).",
            }
        )
    

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
            return Response(
                {"success": False, "message": "Please select 'to_date' when using 'from_date'."},
                status=400
            )

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
        # if status_val is not None:
        #     filters &= Q(is_status=status_val)
        if status_val is not None:
            if status_val == 5:
                filters &= Q(is_status=0, created_at__date=date.today())

            elif status_val == 4:
                # Follow-up scheduled today
                today = date.today()
                loan_qs = EnquiryLoanDetails.objects.filter(followup_pickup_date=today)
                enquiry_ids = loan_qs.values_list("enquiry_id", flat=True).distinct()
                filters &= Q(id__in=enquiry_ids)

            else:
                filters &= Q(is_status=status_val)
        enquiries = Enquiry.objects.filter(filters).order_by("id")
        serializer = EnquirySerializer(enquiries, many=True)

        user_ids = {enq.get("created_by") for enq in serializer.data if enq.get("created_by")}
        users = TblUser.objects.filter(id__in=user_ids).values(
            "id", "full_name", "employee_code", "branch_id"
        )
        user_map = {u["id"]: u for u in users}

        branch_ids = {u["branch_id"] for u in users if u.get("branch_id")}
        branches = TblBranch.objects.filter(id__in=branch_ids).values("id", "branch_name", "branch_code")
        branch_map = {b["id"]: b for b in branches}

        cleaned_data = []
        for enquiry in serializer.data:
            user = user_map.get(enquiry.get("created_by"))
            branch = branch_map.get(user["branch_id"]) if user else None

            row = {
                "Survey Date": enquiry.get("created_at"),
                "Branch Name": branch["branch_name"] if branch else None,
                "Product": None,  
                "Employee Name": user["full_name"] if user else None,
                "Employee Code": user["employee_code"] if user else None,
                "Customer Name": enquiry.get("name"),
                "Business Name": enquiry.get("business_name"),
                "Business Place": enquiry.get("business_place"),
                "Nature of Business": enquiry.get("nature_of_business_display"),
                "Customer Contact": enquiry.get("mobile_number"),
                "Interested": "Yes" if enquiry.get("interested") else "No",
                "KYC Collected": "Yes" if enquiry.get("kyc_collected") else "No",
                "Loan Demand": None,
                "Property Type": None,
                "Property Value": None,
                "Loan Required On": None,
                "Enquiry Type": None,
                "Remark": None,
            }

            if enquiry.get("enquiry_loan_details"):
                loan = enquiry["enquiry_loan_details"][0]
                row.update({
                    "Product": loan.get("loan_type_display"),
                    "Loan Demand": loan.get("loan_amount_range_display"),
                    "Property Type": loan.get("property_type_display"),
                    "Property Value": loan.get("property_value"),
                    "Loan Required On": loan.get("followup_pickup_date"),
                    "Enquiry Type": loan.get("enquiry_type_display"),
                    "Remark": loan.get("remark"),
                })

            cleaned_data.append(row)

        columns = [
            "Survey Date",
            "Branch Name",
            "Product",
            "Employee Name",
            "Employee Code",
            "Customer Name",
            "Business Name",
            "Business Place",
            "Nature of Business",
            "Customer Contact",
            "Interested",
            "KYC Collected",
            "Loan Demand",
            "Property Type",
            "Property Value",
            "Loan Required On",
            "Enquiry Type",
            "Remark",
        ]

        df = pd.DataFrame(cleaned_data)
        df = df[columns] 

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="enquiries_report.xlsx"'
        df.to_excel(response, index=False)
        return response
