from django.http import JsonResponse
from rest_framework.views import APIView

from config_service.authentication import ServiceAuthentication
from config_service.models import Configuration
from config_service.serializers import ConfigurationSerializer


class ConfigurationDetail(APIView):
    authentication_classes = (ServiceAuthentication, )
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer

    def get(self, request):
        merchant_id = request.GET.get('merchant_id')
        handler_type = request.GET.get('handler_type')

        try:
            config_queryset = Configuration.objects.filter(merchant_id=merchant_id, handler_type=handler_type)
            config = config_queryset.values()[0]
        except IndexError:
            return JsonResponse({
                'message': 'configuration for {} using the given handler does not exist.'
                .format(merchant_id)
            }, status=400)

        config['security_credentials'] = [{'type': item.type, 'storage_key': item.storage_key} for item
                                          in config_queryset[0].securitycredential_set.all()]

        return JsonResponse(config, status=200)
