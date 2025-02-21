from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hello_world(request):
    """
    Return a Hello World message to authenticated users
    """
    logger.info(f"Hello World endpoint accessed by user: {request.user.email}")
    return Response({"message": "Hello, World!"})
