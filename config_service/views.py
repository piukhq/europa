from .schemas import StorageKeySchema
from .vault_logic import create_hash, store_key_in_session, get_file_type, upload_to_vault
from config_service.models import Configuration
from config_service.serializers import ConfigurationSerializer
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from sentry_sdk import capture_exception
from voluptuous import MultipleInvalid


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


def prepare_data(request):
    data = {value: request.GET.get(value) for value in request.GET.keys()}

    try:  # Validate payload
        StorageKeySchema(data)
    except MultipleInvalid as e:
        capture_exception(e.error_message)
        return JsonResponse({'error_message': e.error_message})

    storage_key = create_hash(data['credential_type'], data['service_type'], data['merchant_id'])
    key_to_store = data['file']
    is_compound_key = get_file_type(key_to_store)

    vault = upload_to_vault(key_to_store, storage_key, is_compound_key)
    store_key_in_session(request, vault.status_code, storage_key)

    return JsonResponse({}, status=200)


class HealthCheck(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response()
