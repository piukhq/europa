(function($) {
    $(document).ready(function() {

        if (!$) {
            $ = django.jQuery;
        }

        var type_field = $('#id_securityservice_set-0-securitycredential_set-0-type');
        var toggle_elements = $(
            '.key-to-store,' +
            ' .field-key_to_store,' +
            ' .field-storage_key,' +
            ' .storage-key,' +
            ' .upload-button,' +
            ' .upload_to_vault'
        );
        var values = ['bink_private_key', 'bink_public_key', 'merchant_public_key', 'compound_key'];

        function toggleElements(value) {
            if ($.inArray(value, values) !== -1) {
                toggle_elements.show();
            } else {
                toggle_elements.hide();
            }
        }

        //show/hide on load based on pervious value of selectField
        toggleElements(type_field.val());

        // show/hide on change
        type_field.change(function() {
            toggleElements($(this).val());
        });

        type_field.trigger('change');
    })
})(django.jQuery);
