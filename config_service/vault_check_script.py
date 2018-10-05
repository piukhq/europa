from .models import SecurityCredential
import europa.settings as settings
import hvac


client = hvac.Client(url=settings.VAULT_URL, token=settings.VAULT_TOKEN)


def get_vault_items(new_key):
    storage_keys = SecurityCredential.objects.all()
    for key in storage_keys:
        print(client.read('secret/data/{}'.format(key.storage_key)))
    print(client.read('secret/data/{}'.format(new_key)))
