import os
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from auth_system.permissions.token_valid import IsTokenValid
from code_of_conduct.models.deposit_agents import DepositAgents
from code_of_conduct.models.deposit_agents_data import DepositAgentsData
from code_of_conduct.serializers.deposit_agents_serializers import DepositAgentsSerializer
from code_of_conduct.serializers.deposit_agents_data_serializers import DepositAgentsDataSerializer
from code_of_conduct.models.questions import Questions
from rest_framework.response import Response
from django.db import IntegrityError
from rest_framework import status
from django.utils import timezone
from rest_framework.exceptions import NotFound
from auth_system.utils.pagination import CustomPagination
import pandas as pd
import openpyxl
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Q
from auth_system.utils.common import encrypt_id
from auth_system.utils.otp_utils import send_link_to_mobile

class DepositAgentsUploadView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search = request.query_params.get("search", None)

        enquiries = DepositAgentsData.objects.filter(deleted_at__isnull=True)

        if search:
            enquiries = enquiries.filter(
                Q(name__icontains=search) |
                Q(adhar_number__icontains=search) |
                Q(mobile_number__icontains=search) |
                Q(city__icontains=search)
            )

        enquiries = enquiries.order_by("id")

        paginator = CustomPagination()
        page_size = request.query_params.get("page_size")
        page = request.query_params.get("page")

        if page_size or page:
            page_data = paginator.paginate_queryset(enquiries, request)
            serializer = DepositAgentsDataSerializer(page_data, many=True)
            return paginator.get_custom_paginated_response(
                data=serializer.data,
                extra_fields={
                    "success": True,
                    "message": "Deposit agents data retrieved successfully (paginated).",
                },
            )
        else:
            serializer = DepositAgentsDataSerializer(enquiries, many=True)
            return Response({
                "success": True,
                "message": "Deposit agents data retrieved successfully.",
                "data": serializer.data,
            })
    
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"success": False, "message": "No file uploaded."}, status=400)

        # 1. Save file to local folder
        upload_dir = "uploads/deposit_agents/"
        file_name = f"{timezone.now().strftime('%Y%m%d%H%M%S')}_{file.name}"
        file_path = os.path.join(upload_dir, file_name)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # 2. Log the file in database
        deposit_agent = DepositAgents.objects.create(
            deposit_agents_file_upload=file_name,
            created_by=request.user.id,
            created_at=timezone.now()
        )

        try:
            df = pd.read_excel(full_path)

            required_columns = {
                'quarter_code', 'name', 'owner_name', 'from_date', 'to_date',
                'adhar_number', 'pan_number', 'mobile_number', 'city', 'address'
            }

            if not required_columns.issubset(df.columns):
                deposit_agent.delete()
                return Response(
                    {"success": False, "message": "Excel columns are not valid."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            success_count = 0
            duplicate_count = 0
            error_rows = []

            for index, row in df.iterrows():
                try:
                    quarter_code = str(row.get('quarter_code', '')).strip()
                    adhar_number = str(row.get('adhar_number', '')).strip()

                    # Validate mobile length
                    mobile_number = str(row.get('mobile_number', '')).strip()[:15]
                    adhar_number = adhar_number[:20]
                    pan_number = str(row.get('pan_number', '')).strip()[:20]

                    # Convert dates safely
                    from_date = row.get('from_date') if pd.notnull(row.get('from_date')) else None
                    to_date = row.get('to_date') if pd.notnull(row.get('to_date')) else None

                    # Skip if duplicate
                    if DepositAgentsData.objects.filter(quarter_code=quarter_code, adhar_number=adhar_number).exists():
                        duplicate_count += 1
                        continue

                    DepositAgentsData.objects.create(
                        quarter_code=quarter_code,
                        name=str(row.get('name', '')).strip(),
                        owner_name=str(row.get('owner_name', '')).strip(),
                        from_date=from_date,
                        to_date=to_date,
                        adhar_number=adhar_number,
                        pan_number=pan_number,
                        mobile_number=mobile_number,
                        city=str(row.get('city', '')).strip(),
                        address=str(row.get('address', '')).strip(),
                        created_by=request.user.id,
                        created_at=timezone.now()
                    )
                    success_count += 1

                except Exception as e:
                    error_rows.append({"row": index + 2, "error": str(e)})

            return Response({
                "success": True,
                "message": "Upload complete.",
                "summary": {
                    "added": success_count,
                    "duplicates": duplicate_count,
                    "errors": error_rows
                }
            })

        except Exception as e:
            deposit_agent.delete()
            return Response(
                {"success": False, "message": f"Error processing file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class DepositAgentsDataDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return DepositAgentsData.objects.get(pk=pk, deleted_at__isnull=True)
        except DepositAgentsData.DoesNotExist:
            raise NotFound(detail=f"Deposit agents data with id {pk} not found.")

    def get(self, request, pk):
        enquiry = self.get_object(pk)
        serializer = DepositAgentsDataSerializer(enquiry)
        return Response(
            {
                "success": True,
                "message": "Deposit agents data retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        enquiry = self.get_object(pk)
        serializer = DepositAgentsDataSerializer(enquiry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user.id, updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Deposit agents data updated successfully.",
                    # "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update Deposit agents data.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        enquiry = self.get_object(pk)
        enquiry.deleted_at = timezone.now()
        enquiry.deleted_by = request.user.id
        enquiry.save()
        return Response(
            {"success": True, "message": "Deposit agents data deleted successfully."},
            status=status.HTTP_200_OK,
        )
    

class SendLink(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request, pk):
        try:
            deposit_data = DepositAgentsData.objects.get(pk=pk, deleted_at__isnull=True)
        except DepositAgentsData.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Invalid request",
                    "errors": f"DepositAgentsData with id {pk} not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # otp_code, expiry = send_login_otp(user)

        encrypted_id = encrypt_id(pk)
        # Generate the link with the pk
        url = f"https://uatcws.berarfinance.com/deposit_agents/f1/?{encrypted_id}"

        return Response(
            {
                "success": True,
                "message": "Link generated successfully",
                "mobile_number": deposit_data.mobile_number,
                "url": url,
            },
            status=status.HTTP_200_OK,
        )


class SendLinkToMobileView(APIView):
    permission_classes =   [IsAuthenticated, IsTokenValid]

    def post(self, request):
        
        mobile_number = request.data.get("mobile_number")
        link = request.data.get("link")

        if not mobile_number or not link:
            return Response(
                {
                    "success": False,
                    "message": "Invalid request",
                    "errors": "mobile_number and link are required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        api_response  = send_link_to_mobile(request, mobile_number, link)
        
        return Response(
            {
                "success": True,
                "message": "SMS sent successfully" if not api_response.get("error") else "SMS sending failed",
                "sms_api_response": api_response,
            },
            status=status.HTTP_200_OK if not api_response.get("error") else status.HTTP_500_INTERNAL_SERVER_ERROR,
        )