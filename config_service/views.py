from django.http import JsonResponse
from django.contrib.sessions.backends.db import SessionStore
from rest_framework.views import APIView
from rest_framework.response import Response
from config_service.models import Configuration
from config_service.serializers import ConfigurationSerializer
from .forms import SecurityCredentialForm
import ast
import europa.settings as settings
import hashlib
import hvac
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


def prepare_data(request):
    data = {value: request.GET.get(value) for value in request.GET.keys()}
    storage_key = create_hash(data['credential_type'], data['service_type'], data['merchant_id'])
    request.session['storage_key'] = storage_key
    key_to_store = data['file']

    # if type_of_storage_key returns True, the value is a compound key. If False its an RSA key
    type_of_storage_key = get_file_type(key_to_store)
    upload_to_vault(key_to_store, storage_key, type_of_storage_key)
    return JsonResponse({}, status=200)


def create_hash(credential_type, service_type, merchant_id):
    hashed_storage_key = hashlib.sha256(
        "{}.{}.{}".format(
            credential_type, service_type, merchant_id).encode()
    )
    return hashed_storage_key.hexdigest()


def get_file_type(key_to_store):
    try:
        f = ast.literal_eval(key_to_store)
        return isinstance(f, dict)
    except SyntaxError:
        f = False
        return f


def upload_to_vault(key_to_store, storage_key, key_type):
    client = hvac.Client(url=settings.VAULT_URL, token=settings.VAULT_TOKEN)

    if key_type:
        try:  # Save to vault
            client.write('secret/data/{}'.format(storage_key), data=ast.literal_eval(key_to_store))
            print(client.read('secret/data/{}'.format(storage_key)))
        except Exception as e:
            return JsonResponse({e})

    else:
        try:
            client.write('secret/data/{}'.format(storage_key), data={'value': key_to_store})
            print(client.read('secret/data/{}'.format(storage_key)))
        except Exception as e:
            return JsonResponse({e})


class HealthCheck(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response()
