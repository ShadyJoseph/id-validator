import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import NationalIDSerializer
from .authentication import ApiKeyAuthentication
from .permissions import HasApiKey
from .throttling import ApiKeyRateThrottle
from .services import process_validation_request
from .constants import ResponseMessages

logger = logging.getLogger(__name__)


class NationalIDView(APIView):
    """API view for national ID validation."""

    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [HasApiKey]
    throttle_classes = [ApiKeyRateThrottle]

    def post(self, request):
        """Handle national ID validation request."""
        try:
            # Validate request data
            serializer = NationalIDSerializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Invalid request data: {serializer.errors}")
                return Response({
                    "valid": False,
                    "error": "Invalid request data",
                    "details": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            national_id = serializer.validated_data['national_id']

            # Process validation
            result, log_entry = process_validation_request(
                national_id, request.user)

            if result.is_valid:
                response_data = {"valid": True,
                                 "message": ResponseMessages.SUCCESS}
                if result.data:
                    response_data.update(result.data)
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({
                    "valid": False,
                    "error": result.error or ResponseMessages.VALIDATION_FAILED
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(
                f"Unexpected error in NationalIDView: {str(e)}", exc_info=True)
            return Response({
                "valid": False,
                "error": "Internal server error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
