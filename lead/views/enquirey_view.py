from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from auth_system.permissions.token_valid import IsTokenValid
from lead.serializers.enquiry_serializer import EnquirySerializer
from django.db import IntegrityError
from rest_framework import status
from lead.models.enquiry import Enquiry
from django.db.models import Q
from auth_system.utils.pagination import CustomPagination
from rest_framework.exceptions import NotFound
from constants import PercentageStatus
from constants import EnquiryStatus
from lead.models.lead_logs import LeadLog  


class EnquiryListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.query_params.get("search", None)
        count_only = request.query_params.get("count_only") == "true"

        if search_query:
            enquiries = Enquiry.objects.filter(
                Q(name__icontains=search_query) |
                Q(mobile_number__icontains=search_query),
                deleted_at__isnull=True
            )
        else:
            enquiries = Enquiry.objects.filter(deleted_at__isnull=True)
        total_count = enquiries.count()
        if count_only:
            return Response({
                "success": True,
                "message": "Total enquiry count retrieved.",
                "total_count": total_count
            }, status=status.HTTP_200_OK)

        enquiries = enquiries.order_by("id")
        paginator = CustomPagination()
        page_size = request.query_params.get("page_size")
        page = request.query_params.get("page")

        if page or page_size:
            page_data = paginator.paginate_queryset(enquiries, request)
            serializer = EnquirySerializer(page_data, many=True)
            return paginator.get_custom_paginated_response(
                data=serializer.data,
                extra_fields={
                    "success": True,
                    "message": "Enquiries retrieved successfully (paginated).",
                    "total_count": total_count
                }
            )
        else:
            serializer = EnquirySerializer(enquiries, many=True)
            return Response({
                "success": True,
                "message": "Enquiries retrieved successfully.",
                "total_count": total_count,
                "data": serializer.data,
            }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = EnquirySerializer(data=request.data)
        if serializer.is_valid():

            try:
                enquiry = serializer.save(
                    created_by=request.user.id,
                    is_steps=PercentageStatus.ENQUIRY_BASIC,
                    is_status=EnquiryStatus.DRAFT,
                )
                LeadLog.objects.create(
                    enquiry=enquiry,
                    status="Basic Enquiry Form",
                    created_by=request.user.id,
                )
                return Response(
                {
                    "Success": True,
                    "Message": "Enquiry created successfully.",
                    "data": EnquirySerializer(enquiry).data,
                },
                status=status.HTTP_201_CREATED,
                )
            except IntegrityError as e:
                return Response(
                    {
                        "Success": False,
                        "Message": "Integrity error occurred while creating enquiry.",
                        "Error": str(e),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {
                    "Success": False,
                    "Message": "Invalid data provided.",
                    "Errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )   
        

class EnquiryDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]
    def get_object(self, pk):
        try:
            return Enquiry.objects.select_related(
                'enquiry_verification'
            ).prefetch_related(
                'enquiry_addresses',
                'enquiry_loan_details',
                'enquiry_images',
                'enquiry_selfies'
            ).get(pk=pk, deleted_at__isnull=True)
        except Enquiry.DoesNotExist:
            raise NotFound(detail=f"Enquiry with id {pk} not found.")

    def get(self, request, pk):
        enquiry = self.get_object(pk)
        serializer = EnquirySerializer(enquiry)
        return Response(
            {
                "success": True,
                "message": "Enquiry retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
class EnquiryExistingDataAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]
    def post(self, request):
        mobile = request.data.get("mobile_number")
        lan = request.data.get("lan_number")

        if not mobile and not lan:
            return Response({
                "success": False,
                "message": "At least mobile_number or lan_number is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        query = Q(deleted_at__isnull=True)
        if mobile:
            query &= Q(mobile_number=mobile)
        if lan:
            query &= Q(lan_number=lan)
        enquiry = Enquiry.objects.filter(query).order_by("-id").first()
        if not enquiry:
            return Response({
                "success": False,
                "message": "No matching enquiry found."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EnquirySerializer(enquiry)
        return Response({
            "success": True,
            "message": "Latest matching enquiry retrieved.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
