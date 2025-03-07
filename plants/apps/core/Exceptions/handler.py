from rest_framework.views import exception_handler


def common_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data["success"] = False
        response.data["response_code"] = response.status_code
        response.data["response_data"] = None
        response.data["response_message"] = response.data["detail"]
        response.data.pop("detail", None)

    return response
