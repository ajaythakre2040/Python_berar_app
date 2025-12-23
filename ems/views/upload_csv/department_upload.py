import csv
import io
from django.db import transaction, IntegrityError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ems.models.department import TblDepartment
from ems.serializers.department_serializers import TblDepartmentSerializer


class DepartmentCSVUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # --- 1. FILE LEVEL ERRORS ---
        if "file" not in request.FILES:
            return Response(
                {"error": "File nahi mili. Please 'file' key mein upload karein."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file = request.FILES["file"]

        if not file.name.endswith(".csv"):
            return Response(
                {"error": "Sirf .csv files allowed hain."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success_rows = []
        error_rows = []

        try:
            # --- 2. ENCODING ERRORS ---
            # utf-8-sig Excel ke special characters (BOM) ko handle karta hai
            decoded_file = file.read().decode("utf-8-sig")
            csv_data = io.StringIO(decoded_file)
            csv_reader = csv.DictReader(csv_data)

            # --- 3. COLUMN/HEADER ERRORS ---
            required_columns = ["department_name"]
            if not csv_reader.fieldnames or not all(
                col in csv_reader.fieldnames for col in required_columns
            ):
                missing = [
                    c
                    for c in required_columns
                    if c not in (csv_reader.fieldnames or [])
                ]
                return Response(
                    {"error": f"CSV headers missing: {missing}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # --- 4. ROW LEVEL ERRORS ---
            for index, row in enumerate(csv_reader, start=1):
                # Safai: Extra spaces hatana aur empty ko None banana
                data = {k: (v.strip() if v else None) for k, v in row.items()}
                dept_name = data.get("department_name")

                try:
                    with transaction.atomic():
                        # Serializer validation (Duplicate name/email check yahi se hoga)
                        serializer = TblDepartmentSerializer(data=data)

                        if serializer.is_valid():
                            # created_by IntegerField hai isliye .id bhej rahe hain
                            serializer.save(created_by=request.user.id)
                            success_rows.append(dept_name)
                        else:
                            # Validation failure (e.g. Duplicate name)
                            error_rows.append(
                                {
                                    "row": index,
                                    "name": dept_name or "Row No " + str(index),
                                    "errors": serializer.errors,
                                }
                            )

                except IntegrityError as ie:
                    error_rows.append(
                        {
                            "row": index,
                            "errors": f"Database Constraint Error: {str(ie)}",
                        }
                    )
                except Exception as e:
                    error_rows.append(
                        {"row": index, "errors": f"Unexpected Row Error: {str(e)}"}
                    )

            # --- 5. RESPONSE SUMMARY ---
            # Agar sab success hai toh 200, agar mix hai toh 207, agar sab fail toh 400
            final_status = status.HTTP_200_OK
            if error_rows and success_rows:
                final_status = status.HTTP_207_MULTI_STATUS
            elif error_rows and not success_rows:
                final_status = status.HTTP_400_BAD_REQUEST

            return Response(
                {
                    "message": "Processing complete",
                    "summary": {
                        "total": len(success_rows) + len(error_rows),
                        "success": len(success_rows),
                        "failed": len(error_rows),
                    },
                    "success_data": success_rows,
                    "failed_data": error_rows,
                },
                status=final_status,
            )

        except UnicodeDecodeError:
            return Response(
                {"error": "File encoding galat hai. Please UTF-8 CSV use karein."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as fatal_e:
            return Response(
                {"error": f"Server Fatal Error: {str(fatal_e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
