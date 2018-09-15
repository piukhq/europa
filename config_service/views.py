from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from config_service.models import Configuration
from config_service.serializers import ConfigurationSerializer
import hashlib
from django.views.decorators.csrf import csrf_exempt
import json


class ConfigurationDetail(APIView):
    # authentication_classes = (ServiceAuthentication, )
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

        inbound_security_service = config_queryset[0].securityservice_set.get(request_type="INBOUND")
        outbound_security_service = config_queryset[0].securityservice_set.get(request_type="OUTBOUND")

        inbound_credentials = {
            'service': inbound_security_service.type,
            'credentials': [{
                'credential_type': item.type,
                'storage_key': item.storage_key}
                for item in inbound_security_service.securitycredential_set.all()]
        }

        outbound_credentials = {
            'service': outbound_security_service.type,
            'credentials': [{
                'credential_type': item.type,
                'storage_key': item.storage_key}
                for item in outbound_security_service.securitycredential_set.all()]
        }

        config['security_credentials'] = {'inbound': inbound_credentials, 'outbound': outbound_credentials}

        return JsonResponse(config, status=200)


@csrf_exempt
def upload_to_vault(request):
    data = request.GET
    # credentials_from_data = json.loads(data)
    storage_key = create_hash(credentials_from_data)
    file = request.FILES['file']
    pass


def create_hash(data):
    hashed_storage_key = hashlib.sha256(
        "{}.{}.{}".format(
            data['credential_type'], data['service_type'], data['merchant_id']).encode()
    )
    return hashed_storage_key.hexdigest()


class HealthCheck(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response()
