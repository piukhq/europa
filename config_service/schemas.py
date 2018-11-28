from voluptuous import All, Length, Required, Schema

# Schemas
StorageKeySchema = Schema({
    Required('csrfmiddlewaretoken'): All(str, Length(min=1)),
    Required('form_data[merchant_id]'): All(str, Length(min=1)),
    Required('form_data[service_type]'): All(str, Length(min=1)),
    Required('form_data[credential_type]'): All(str, Length(min=1)),
    Required('form_data[file]'): All(str, Length(min=1)),
})
