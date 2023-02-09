from rest_framework.views import exception_handler
from django.http import Http404


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        if isinstance(exc, Http404):
            custom_response_data = {
                'detail': 'This object does not exist.'  # custom exception message
            }
            response.data = custom_response_data  # set the custom response data on response object
        response.data['code'] = response.status_code
        response.data['message'] = response.data.get('detail')
        del response.data['detail']
        if response.data.get('messages', ''):
            del response.data['messages']
        return response
