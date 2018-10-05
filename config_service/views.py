from config_service.models import Configuration
from config_service.serializers import ConfigurationSerializer
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .schemas import StorageKeySchema
from sentry_sdk import capture_exception
from voluptuous import MultipleInvalid
from .vault_check_script import get_vault_items
import ast
import europa.settings as settings
import hashlib
import hvac


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

    try:
        StorageKeySchema(data)
    except MultipleInvalid as e:
        capture_exception(e)
        return Response(e)

    storage_key = create_hash(data['credential_type'], data['service_type'], data['merchant_id'])
    key_to_store = data['file']

    # if is_compound_key returns True, the compound key is a dictionary. If False the RSA key is string.
    is_compound_key = get_file_type(key_to_store)
    vault = upload_to_vault(key_to_store, storage_key, is_compound_key)

    if vault.status_code != 201:
        request.session['storage_key'] = vault.data
    else:
        request.session['storage_key'] = storage_key

    return JsonResponse({}, status=200)


def create_hash(credential_type, service_type, merchant_id):
    hashed_storage_key = hashlib.sha256(
        "{}.{}.{}".format(
            credential_type, service_type, merchant_id).encode()
    )
    return hashed_storage_key.hexdigest()


def get_file_type(key_to_store):
    try:  # if key_to_store is a dict we know we have a compound key
        return isinstance(ast.literal_eval(key_to_store), dict)
    except SyntaxError:
        return False


def upload_to_vault(key_to_store, storage_key, is_compound_key):
    client = hvac.Client(url=settings.VAULT_URL, token=settings.VAULT_TOKEN)

    if is_compound_key:
        try:  # Save to vault
            client.write('secret/data/{}'.format(storage_key), data=ast.literal_eval(key_to_store))
            get_vault_items(storage_key)
            return Response(status=201, data='Saved to vault')

        except Exception as e:
            capture_exception(e)
            return Response(e.errors[0])

    else:
        try:
            client.write('secret/data/{}'.format(storage_key), data={'value': key_to_store})
            get_vault_items(storage_key)
            return Response(status=201, data='Saved to vault')

        except Exception as e:
            capture_exception(e)
            return Response(e.errors[0])


class HealthCheck(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response()
