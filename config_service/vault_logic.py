from .vault_check_script import get_vault_items
from .vault_connector import connect_to_vault
from rest_framework.response import Response
from sentry_sdk import capture_exception
import ast
import hashlib


def create_hash(credential_type, service_type, merchant_id):
    hashed_storage_key = hashlib.sha256(
        "{}.{}.{}".format(
            credential_type, service_type, merchant_id).encode()
    )
    return hashed_storage_key.hexdigest()


def store_key_in_session(request, vault_status_code, storage_key):
    if vault_status_code != 201:
        request.session['storage_key'] = vault_status_code.data
    else:
        request.session['storage_key'] = storage_key


def get_file_type(key_to_store):
    try:  # if key_to_store is a dict we know we have a compound key
        return isinstance(ast.literal_eval(key_to_store), dict)
    except SyntaxError:
        return False
    except ValueError:
        return False


def upload_to_vault(key_to_store, storage_key, is_compound_key):
    client = connect_to_vault()
    if is_compound_key:
        try:  # Save to vault
            client.write('secret/data/{}'.format(storage_key), data=ast.literal_eval(key_to_store))
            get_vault_items(storage_key)
            return Response(status=201, data='Saved to vault')

        except Exception as e:
            capture_exception(e)
            return Response(e)

    else:
        try:
            client.write('secret/data/{}'.format(storage_key), data={'value': key_to_store})
            get_vault_items(storage_key)
            return Response(status=201, data='Saved to vault')

        except Exception as e:
            capture_exception(e)
            return Response(e)
