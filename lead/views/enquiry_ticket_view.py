from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from auth_system.permissions.token_valid import IsTokenValid
from ..serializers.enquiry_tickets_serializers import EnquiryTicketSerializer
from ..models.enquiry_tickets import EnquiryTickets
from django.shortcuts import get_object_or_404
from auth_system.utils.pagination import CustomPagination


class EnquiryTicketCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]
    def post(self, request):
        serializer = EnquiryTicketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.id)
            return Response(
                {
                    "success": True,
                    "data": serializer.data,
                    "message": "Ticket created successfully",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def get(self, request):
        tickets = EnquiryTickets.objects.filter(deleted_at__isnull=True).order_by("-id")
        total_count = tickets.count()
        count_only = request.query_params.get("count_only") == "true"
        if count_only:
            return Response(
                {
                    "success": True,
                    "message": "Total enquiry ticket count retrieved.",
                    "total_counts": total_count,
                },
                status=status.HTTP_200_OK,
            )
        
        paginator = CustomPagination()
        page_data = paginator.paginate_queryset(tickets, request)
        if page_data is not None:
            serializer = EnquiryTicketSerializer(page_data, many=True)
            return paginator.get_custom_paginated_response(
                data=serializer.data,
                extra_fields={
                    "success": True,
                    "message": "Tickets retrieved successfully (paginated).",
                    "total_count": total_count,
                },
            )
        # If no pagination
        serializer = EnquiryTicketSerializer(tickets, many=True)
        return Response(
            {
                "success": True,
                "data": serializer.data,
                "message": "Tickets retrieved successfully",
                "total_count": total_count,
            },
            status=status.HTTP_200_OK,
        )
class EnquiryTicketDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]
    def get(self, request, ticket_id):
        # Fetch ticket or return 404
        ticket = get_object_or_404(
            EnquiryTickets, pk=ticket_id, deleted_at__isnull=True
        )
        serializer = EnquiryTicketSerializer(ticket, context={"request": request})
        return Response(
            {
                "success": True,
                "data": serializer.data,
                "message": "Ticket retrieved successfully",
            },
            status=status.HTTP_200_OK,
        )
    def patch(self, request, ticket_id):
        ticket = get_object_or_404(
            EnquiryTickets, pk=ticket_id, deleted_at__isnull=True
        )
        new_status = request.data.get("status")
        if new_status is None:
            return Response(
                {"success": False, "message": "Status is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            new_status = int(new_status)
        except (TypeError, ValueError):
            return Response(
                {"success": False, "message": "Status must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Validate status against model choices
        valid_statuses = [
            choice[0] for choice in EnquiryTickets._meta.get_field("status").choices
        ]
        if new_status not in valid_statuses:
            return Response(
                {
                    "success": False,
                    "message": f"Invalid status. Allowed values: {valid_statuses}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        ticket.status = new_status
        ticket.updated_by = request.user.id
        ticket.save()
        serializer = EnquiryTicketSerializer(ticket, context={"request": request})
        return Response(
            {
                "success": True,
                "data": serializer.data,
                "message": "Status updated successfully.",
            },
            status=status.HTTP_200_OK,
        )