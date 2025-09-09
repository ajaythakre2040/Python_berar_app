# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework import status
# from django.utils.dateparse import parse_date
# from django.db.models import Q

# from auth_system.permissions.token_valid import IsTokenValid
# from lead.models.enquiry import Enquiry


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
#             return Response({
#                 "success": False,
#                 "message": "Please select 'to_date' when using 'from_date'."
#             }, status=status.HTTP_400_BAD_REQUEST)

#         if to_date:
#             to_date = parse_date(to_date)
#             if not to_date:
#                 return Response({"success": False, "message": "Invalid 'to_date' format. Use YYYY-MM-DD."},
#                                 status=status.HTTP_400_BAD_REQUEST)

#             if from_date:
#                 from_date = parse_date(from_date)
#                 if not from_date:
#                     return Response({"success": False, "message": "Invalid 'from_date' format. Use YYYY-MM-DD."},
#                                     status=status.HTTP_400_BAD_REQUEST)

#                 filters &= Q(created_at__date__range=[from_date, to_date])

#             else:
#                 filters &= Q(created_at__date=to_date)


#         if employee_id:
#             filters &= Q(created_by=employee_id)

#         if assign_to:
#             filters &= Q(assign_to=assign_to)

#         if status_val is not None:
#             filters &= Q(is_status=status_val)

#         enquiries = Enquiry.objects.filter(filters).values(
#             "id", "name", "mobile_number", "created_by", "assign_to", "is_status", "created_at"
#         )
        

#         return Response({
#             "success": True,
#             "count": enquiries.count(),
#             "results": list(enquiries)
#         }, status=status.HTTP_200_OK)

# this one is also working :



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
