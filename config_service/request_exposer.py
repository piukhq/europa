from config_service import models


def ExposeRequestMiddleware(get_response):
    def middleware(request):
        models.exposed_request = request
        response = get_response(request)
        return response

    return middleware
