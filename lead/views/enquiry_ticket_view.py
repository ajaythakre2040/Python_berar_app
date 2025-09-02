from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from auth_system.permissions.token_valid import IsTokenValid
from ..serializers.enquiry_tickets_serializers import EnquiryTicketSerializer
from ..models.enquiry_tickets import EnquiryTickets
from django.shortcuts import get_object_or_404

class EnquiryTicketCreateAPIView(APIView):

    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request):
        serializer   =  EnquiryTicketSerializer(data=request.data)
        if serializer.is_valid():

            serializer.save(created_by=request.user.id)

            return Response({
                "success":True,
                "data":serializer.data,
                "message":"Ticket created successfully"
            }, status=status.HTTP_201_CREATED)
        
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

    def get(self, request):
        tickets = EnquiryTickets.objects.filter(deleted_at__isnull=True).order_by("-created_at")
        serializer = EnquiryTicketSerializer(tickets, many=True)
        return Response(
            {"success": True, "data": serializer.data, "message": "Tickets retrieved successfully"},
            status=status.HTTP_200_OK,
        )
    
class EnquiryTicketDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request, ticket_id):
        # Fetch ticket or return 404
        ticket = get_object_or_404(EnquiryTickets, pk=ticket_id, deleted_at__isnull=True)
        serializer = EnquiryTicketSerializer(ticket, context={"request": request})
        return Response(
            {"success": True, "data": serializer.data, "message": "Ticket retrieved successfully"},
            status=status.HTTP_200_OK,
        )