import europa.settings as settings
import hvac


def connect_to_vault():
    client = hvac.Client(url=settings.VAULT_URL, token=settings.VAULT_TOKEN)
    return client
