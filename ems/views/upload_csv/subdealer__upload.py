import csv
import io
from django.db import transaction, IntegrityError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ems.models import SubDealer, Dealer
from ems.serializers.subdealer_serializer import SubDealerSerializer
# from ems.serializers.subdealer_serializers import SubDealerSerializer


class SubDealerCSVUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # 1. File availability check
        if "file" not in request.FILES:
            return Response(
                {"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES["file"]

        # 2. File format check
        if not file.name.endswith(".csv"):
            return Response(
                {"error": "Only CSV files are allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success_rows = []
        error_rows = []

        try:
            # 3. Decode handling (utf-8-sig handles Excel BOM)
            decoded_file = file.read().decode("utf-8-sig")
            csv_data = io.StringIO(decoded_file)
            csv_reader = csv.DictReader(csv_data)

            # 4. Mandatory Headers Check
            required_headers = [
                "code",
                "name",
                "dealer_id",
                "branch_id",
                "mobile_number",
            ]
            if not csv_reader.fieldnames or not all(
                h in csv_reader.fieldnames for h in required_headers
            ):
                missing = [
                    h
                    for h in required_headers
                    if h not in (csv_reader.fieldnames or [])
                ]
                return Response(
                    {"error": f"CSV missing headers: {missing}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 5. Row-by-Row Processing
            for index, row in enumerate(csv_reader, start=1):
                # Cleaning data (strip extra spaces)
                data = {k: (v.strip() if v else None) for k, v in row.items()}
                subdealer_code = data.get("code")

                try:
                    with transaction.atomic():
                        # Serializer duplicate code aur dealer_id validity check karega
                        serializer = SubDealerSerializer(data=data)

                        if serializer.is_valid():
                            # Save with the ID of the logged-in user
                            serializer.save(created_by=request.user.id)
                            success_rows.append(subdealer_code)
                        else:
                            error_rows.append(
                                {
                                    "row_index": index,
                                    "identifier": subdealer_code or "Unknown",
                                    "errors": serializer.errors,
                                }
                            )

                except IntegrityError as ie:
                    error_rows.append(
                        {"row_index": index, "errors": f"Database Conflict: {str(ie)}"}
                    )
                except Exception as e:
                    error_rows.append(
                        {"row_index": index, "errors": f"System error: {str(e)}"}
                    )

            # 6. Response Strategy
            res_status = status.HTTP_200_OK
            if error_rows and success_rows:
                res_status = status.HTTP_207_MULTI_STATUS
            elif error_rows and not success_rows:
                res_status = status.HTTP_400_BAD_REQUEST

            return Response(
                {
                    "message": "SubDealer CSV upload complete.",
                    "summary": {
                        "total_rows": len(success_rows) + len(error_rows),
                        "success": len(success_rows),
                        "failed": len(error_rows),
                    },
                    "success_codes": success_rows,
                    "error_details": error_rows,
                },
                status=res_status,
            )

        except Exception as fatal_e:
            return Response(
                {"error": f"Fatal server error: {str(fatal_e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
