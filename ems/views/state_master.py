from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ems.models import State
from ems.serializers import StateSerializer


class StateListCreateAPIView(APIView):
    def get(self, request):
        states = State.objects.select_related("country").all()
        serializer = StateSerializer(states, many=True)
        return Response(
            {
                "success": True,
                "message": "State list fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = StateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "State created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to create state.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class StateDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return State.objects.select_related("country").get(pk=pk)
        except State.DoesNotExist:
            return None

    def get(self, request, pk):
        state = self.get_object(pk)
        if not state:
            return Response(
                {"success": False, "message": "State not found."}, status=404
            )
        serializer = StateSerializer(state)
        return Response(
            {
                "success": True,
                "message": "State fetched successfully.",
                "data": serializer.data,
            }
        )

    def patch(self, request, pk):
        state = self.get_object(pk)
        if not state:
            return Response(
                {"success": False, "message": "State not found."}, status=404
            )
        serializer = StateSerializer(state, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "State updated successfully.",
                    "data": serializer.data,
                }
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update state.",
                "errors": serializer.errors,
            },
            status=400,
        )

    def delete(self, request, pk):
        state = self.get_object(pk)
        if not state:
            return Response(
                {"success": False, "message": "State not found."}, status=404
            )
        state.delete()
        return Response(
            {"success": True, "message": "State deleted successfully."}, status=204
        )
