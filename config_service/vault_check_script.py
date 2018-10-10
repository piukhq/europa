from .models import SecurityCredential
from .vault_connector import connect_to_vault


client = connect_to_vault()


def get_vault_items(new_key):
    storage_keys = SecurityCredential.objects.all()
    for key in storage_keys:
        print(client.read('secret/data/{}'.format(key.storage_key)))
    print(client.read('secret/data/{}'.format(new_key)))
