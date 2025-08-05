from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ems.models import City
from ems.serializers.location_master_serializers import CitySerializer


class CityMasterListCreateAPIView(APIView):
    def get(self, request):
        cities = City.objects.all()
        serializer = CitySerializer(cities, many=True)
        return Response(
            {
                "success": True,
                "message": "CityMaster list fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = CitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "CityMaster created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to create CityMaster.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class CityMasterDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return City.objects.get(pk=pk)
        except City.DoesNotExist:
            return None

    def get(self, request, pk):
        city = self.get_object(pk)
        if not city:
            return Response(
                {"success": False, "message": "CityMaster not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CitySerializer(city)
        return Response(
            {
                "success": True,
                "message": "CityMaster retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        city = self.get_object(pk)
        if not city:
            return Response(
                {"success": False, "message": "CityMaster not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CitySerializer(city, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "CityMaster updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update CityMaster.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        city = self.get_object(pk)
        if not city:
            return Response(
                {"success": False, "message": "CityMaster not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        city.delete()
        return Response(
            {"success": True, "message": "CityMaster deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
