from voluptuous import All, ALLOW_EXTRA, Invalid, Length, Optional, Required, Schema

# Schemas
StorageKeySchema = Schema({
    Required('merchant_id'): All(str, Length(min=1)),
    Required('service_type'): All(str, Length(min=1)),
    Required('credential_type'): All(str, Length(min=1)),
    Required('file'): All(str, Length(min=1)),
})
