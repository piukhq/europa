from enum import Enum


class SecurityCredentialTypes(Enum):
    BINK_PRIVATE_KEY = ("bink_private_key", "Bink private key")
    BINK_PUBLIC_KEY = ("bink_public_key", "Bink public key")
    MERCHANT_PUBLIC_KEY = ("merchant_public_key", "Merchant public key")
    COMPOUND_KEY = ("compound_key", "Compound key")
