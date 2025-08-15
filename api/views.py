import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import NationalIDSerializer
from .authentication import ApiKeyAuthentication
from .permissions import HasApiKey
from .throttling import ApiKeyRateThrottle
from .services import process_validation_request

logger = logging.getLogger(__name__)


class NationalIDView(APIView):
    """API view for national ID validation."""

    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [HasApiKey]
    throttle_classes = [ApiKeyRateThrottle]

    def post(self, request):
        """Handle national ID validation request."""
        serializer = NationalIDSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Invalid request data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        national_id = serializer.validated_data['national_id']

        try:
            result, log_entry = process_validation_request(
                national_id, request.user)

            if result.is_valid:
                return Response({"valid": True, **result.data}, status=status.HTTP_200_OK)
            else:
                return Response({"valid": False, "error": result.error}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Unexpected error in view: {str(e)}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
