# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from auth_system.permissions.token_valid import IsTokenValid



# class EnquiryReportAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsTokenValid]

#     def get(self, request):

#         data = request.data

#         to_date = data.get("to_date")
#         from_date = data.get("from_date")
#         employee_id = data.get("employee_id")
#         assign_to = data.get("assign_to")
#         status = data.get("status")



#         return Response({
#             "success": True,
#             "message": "Enquiry report endpoint is under construction."
#         }, status=status.HTTP_200_OK)