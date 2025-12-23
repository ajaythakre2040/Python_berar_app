import csv
import io
from django.db import transaction, IntegrityError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ems.models import Dealer
from ems.serializers.dealer_serializer import DealerSerializer


class DealerCSVUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # 1. Check if file exists
        if "file" not in request.FILES:
            return Response(
                {"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES["file"]

        if not file.name.endswith(".csv"):
            return Response(
                {"error": "Please upload a valid CSV file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success_rows = []
        error_rows = []

        try:
            # 2. Decode with utf-8-sig for Excel compatibility
            decoded_file = file.read().decode("utf-8-sig")
            csv_data = io.StringIO(decoded_file)
            csv_reader = csv.DictReader(csv_data)

            # 3. Required Headers Validation
            # 'code' aur 'name' base fields hain
            required_headers = ["branch_id", "code", "name", "mobile_number", "email"]
            if not csv_reader.fieldnames or not all(
                h in csv_reader.fieldnames for h in required_headers
            ):
                missing = [
                    h
                    for h in required_headers
                    if h not in (csv_reader.fieldnames or [])
                ]
                return Response(
                    {"error": f"CSV headers missing: {missing}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 4. Loop through rows
            for index, row in enumerate(csv_reader, start=1):
                # Cleaning data
                data = {k: (v.strip() if v else None) for k, v in row.items()}
                dealer_code = data.get("code")

                try:
                    with transaction.atomic():
                        # Duplicate 'code' check manually for a better error message
                        if Dealer.objects.filter(code=dealer_code).exists():
                            error_rows.append(
                                {
                                    "row": index,
                                    "code": dealer_code,
                                    "errors": f"Dealer code '{dealer_code}' already exists.",
                                }
                            )
                            continue

                        serializer = DealerSerializer(data=data)
                        if serializer.is_valid():
                            # created_by IntegerField hai, isliye request.user.id pass karein
                            serializer.save(created_by=request.user.id)
                            success_rows.append(dealer_code)
                        else:
                            error_rows.append(
                                {
                                    "row": index,
                                    "code": dealer_code or "Unknown",
                                    "errors": serializer.errors,
                                }
                            )

                except IntegrityError as ie:
                    error_rows.append(
                        {"row": index, "errors": f"Database Conflict: {str(ie)}"}
                    )
                except Exception as e:
                    error_rows.append({"row": index, "errors": str(e)})

            # 5. Result Summary
            return Response(
                {
                    "message": "Dealer CSV processing complete.",
                    "total": len(success_rows) + len(error_rows),
                    "success_count": len(success_rows),
                    "error_count": len(error_rows),
                    "errors": error_rows,
                },
                status=(
                    status.HTTP_207_MULTI_STATUS
                    if error_rows and success_rows
                    else status.HTTP_200_OK
                ),
            )

        except Exception as fatal_e:
            return Response(
                {"error": f"Fatal error: {str(fatal_e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
