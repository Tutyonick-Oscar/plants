from rest_framework.decorators import api_view
from rest_framework.response import Response

from plants.apps.core.models import RequestOffset


@api_view(["POST"])
def init_request_offset(request):
    """
    This view make a post request to initialize request offset to 0
    For pernual api limitation purposes
    Args:
        request (_type_): Post

    Returns:
        _type_: JsonResponse
    """
    offset = RequestOffset()
    offset.save()
    return Response(
        {
            "success": True,
            "response_code": "00",
            "response_data": None,
            "response_message": f"offset initialized to {offset.offset} successfuly !",
        }
    )
