from voluptuous import All, Length, Required, Schema

# Schemas
StorageKeySchema = Schema({
    Required('csrfmiddlewaretoken'): All(str, Length(min=1)),
    Required('merchant_id'): All(str, Length(min=1)),
    Required('service_type'): All(str, Length(min=1)),
    Required('handler_type'): All(str, Length(min=1)),
    Required('credential_type'): All(str, Length(min=1)),
    Required('file'): All(str, Length(min=1)),
})
