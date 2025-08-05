from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import NotFound
from django.utils import timezone

from auth_system.models.user import TblUser
from auth_system.serializers.user_serializer import TblUserSerializer
from ems.models import TblEmpOfficialInformation
from ems.models.emp_basic_profile import TblEmpBasicProfile
from ems.models.user_branches import UserBranches
from ems.serializers import TblEmpOfficialInformationSerializer
from auth_system.permissions.token_valid import IsTokenValid
from ems.serializers.user_branches_serializer import UserBranchesSerializer
from ems.utils.password_generator import generate_password
from auth_system.utils.pagination import CustomPagination
from django.db import transaction
from rest_framework import serializers


class EmpOfficialInfoView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        official_infos = TblEmpOfficialInformation.objects.filter(
            deleted_at__isnull=True
        ).order_by("id")
        paginator = CustomPagination()
        page = paginator.paginate_queryset(official_infos, request)
        serializer = TblEmpOfficialInformationSerializer(page, many=True)

        return paginator.get_custom_paginated_response(
            data=serializer.data,
            extra_fields={
                "success": True,
                "message": "Official information fetched successfully.",
            },
        )

    def post(self, request):
        user_id = request.user.id
        data = request.data
        employee_id = data.get("employee_id")

        if not employee_id:
            return Response(
                {"success": False, "message": "Employee ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            employee_basic = TblEmpBasicProfile.objects.get(id=employee_id, deleted_at__isnull=True)
        except TblEmpBasicProfile.DoesNotExist:
            return Response(
                {"success": False, "message": "Employee basic details not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if TblEmpOfficialInformation.objects.filter(employee_id=employee_id, deleted_at__isnull=True).exists():
            return Response(
                {"success": False, "message": "Official info already exists for this employee."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if TblUser.objects.filter(employee_id=employee_id, deleted_at__isnull=True).exists():
            return Response(
                {"success": False, "message": "User already exists for this employee."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        password_result = generate_password(employee_basic.name, employee_basic.mobile_number)
        if not password_result["valid"]:
            return Response(
                {"success": False, "message": password_result["message"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        password = password_result["password"]

        try:
            with transaction.atomic():
                # Step 1: Create user
                user_data = {
                    "role_id": data.get("role_id"),
                    "employee_id": employee_id,
                    "employee_code": employee_basic.employee_code,
                    "branch_id": data.get("branch_id"),
                    "department_id": data.get("department_id"),
                    "designation_id": data.get("designation_id"),
                    "level": data.get("level"),
                    "full_name": employee_basic.name,
                    "email": employee_basic.email,
                    "mobile_number": employee_basic.mobile_number,
                    "password": password,
                    "confirm_password": password,
                    "two_step": data.get("two_step", False),
                    "created_by": user_id,
                }

                user_serializer = TblUserSerializer(data=user_data)
                user_serializer.is_valid(raise_exception=True)
                user_serializer.save()

                # Step 2: Multibranch assignment
                multibranch_ids = data.get("multibranch_id")
                if multibranch_ids and isinstance(multibranch_ids, str):
                    branch_ids = [
                        int(branch.strip())
                        for branch in multibranch_ids.strip("[]").split(",")
                        if branch.strip().isdigit()
                    ]
                    if branch_ids:
                        user_branch_data = [
                            {
                                "employee_id": employee_id,
                                "branch_id": branch_id,
                                "created_by": user_id,
                            }
                            for branch_id in branch_ids
                        ]
                        branch_serializer = UserBranchesSerializer(data=user_branch_data, many=True)
                        branch_serializer.is_valid(raise_exception=True)
                        branch_serializer.save()

                # Step 3: Official information
                official_data = {
                    "employee_id": employee_id,
                    "reporting_to": data.get("reporting_to"),
                    "employment_status": data.get("employment_status"),
                    "remarks": data.get("remarks"),
                    "profile_photo": data.get("profile_photo"),
                    "signature": data.get("signature"),
                    "created_by": user_id,
                }

                official_serializer = TblEmpOfficialInformationSerializer(data=official_data)
                official_serializer.is_valid(raise_exception=True)
                official_serializer.save()

                return Response(
                    {
                        "success": True,
                        "message": "Employee official information created successfully.",
                    },
                    status=status.HTTP_201_CREATED,
                )

        except serializers.ValidationError as ve:
            return Response(
                {"success": False, "message": "Validation failed.", "errors": ve.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"success": False, "message": "An unexpected error occurred.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class EmpOfficialInfoDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, employee_id):
        try:
            return TblEmpOfficialInformation.objects.get(
                employee_id=employee_id, deleted_at__isnull=True
            )
        except TblEmpOfficialInformation.DoesNotExist:
            raise NotFound("Official info not found.")

    def get(self, request, employee_id):
        official_info = self.get_object(employee_id)
        serializer = TblEmpOfficialInformationSerializer(official_info)

        return Response(
            {
                "success": True,
                "message": "Employee official info retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, employee_id):
        user_id = request.user.id
        data = request.data

        official_instance = self.get_object(employee_id)
        official_serializer = TblEmpOfficialInformationSerializer(
            official_instance, data=data, partial=True
        )
        if not official_serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Failed to update official information.",
                    "errors": official_serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        official_serializer.save(updated_by=user_id, updated_at=timezone.now())

        # Update linked user fields if user exists
        user_instance = TblUser.objects.filter(
            employee_id=employee_id, deleted_at__isnull=True
        ).first()
        if user_instance:
            user_fields = [
                "role_id",
                "branch_id",
                "department_id",
                "designation_id",
                "level",
                "two_step",
            ]
            for field in user_fields:
                if field in data:
                    value = data[field]
                    if field == "two_step":
                        if isinstance(value, str):
                            value = value.strip().lower() == "true"
                        else:
                            value = bool(value)
                    setattr(user_instance, field, value)
            user_instance.updated_by = user_id
            user_instance.updated_at = timezone.now()
            user_instance.save()

        # Handle multibranch_ids updates
        multibranch_ids = data.get("multibranch_id")
        if isinstance(multibranch_ids, str):
            try:
                multibranch_ids = [
                    int(branch.strip())
                    for branch in multibranch_ids.strip("[]").split(",")
                    if branch.strip().isdigit()
                ]
            except Exception:
                multibranch_ids = []

        if isinstance(multibranch_ids, list) and multibranch_ids:
            multibranch_ids = list(set(multibranch_ids))  # unique branches

            existing_branch_ids = set(
                UserBranches.objects.filter(
                    employee_id=employee_id, deleted_at__isnull=True
                ).values_list("branch_id", flat=True)
            )

            # Remove branches no longer assigned
            to_remove = existing_branch_ids - set(multibranch_ids)
            if to_remove:
                UserBranches.objects.filter(
                    employee_id=employee_id,
                    branch_id__in=to_remove,
                    deleted_at__isnull=True,
                ).update(
                    deleted_at=timezone.now(),
                    deleted_by=user_id,
                    updated_by=user_id,
                    updated_at=timezone.now(),
                )

            # Add new branches
            to_add = set(multibranch_ids) - existing_branch_ids
            if to_add:
                new_branches = [
                    {
                        "employee_id": employee_id,
                        "branch_id": branch_id,
                        "created_by": user_id,
                    }
                    for branch_id in to_add
                ]
                branch_serializer = UserBranchesSerializer(data=new_branches, many=True)
                if not branch_serializer.is_valid():
                    return Response(
                        {
                            "success": False,
                            "message": "Failed to assign branches.",
                            "errors": branch_serializer.errors,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                branch_serializer.save()

        return Response(
            {
                "success": True,
                "message": "Employee official information updated successfully.",
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, employee_id):
        instance = self.get_object(employee_id)
        instance.deleted_at = timezone.now()
        instance.deleted_by = request.user.id
        instance.save()
        return Response(
            {"success": True, "message": "Official info deleted successfully."},
            status=status.HTTP_200_OK,
        )
