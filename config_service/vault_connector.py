import europa.settings as settings
import hvac


def connect_to_vault():
    return hvac.Client(url=settings.VAULT_URL, token=settings.VAULT_TOKEN)
