(function($) {
    $(document).ready(function() {

        if (!$) {
            $ = django.jQuery;
        }

        var form_data = {};

        // Upload to vault button is clicked
        $('#upload_to_vault').click(function() {

            form_data['merchant_id'] = $('#id_merchant_id').val();
            form_data['service_type'] = $('#id_securityservice_set-0-type').val();
            form_data['credential_type'] = $('#id_securityservice_set-0-securitycredential_set-0-type').val();

            check_dict(form_data)
        });

        // Check form_data has all data needed to create hash
        function check_dict(form_data) {
            var count = 0;
            for (var data in form_data) {
                if (form_data.hasOwnProperty(data)) count++;
            }

            if (count >= 3){
                send_data(form_data)
            } else {
                alert("Select Merchant ID; Security Services Request Type; Security Credentials Type")
            }
        }

        // Ajax send data to django
        function send_data(form_data) {
            $.get({
                url: '/form_data/',
                contentType: 'json',
                data: {
                    'form_data': JSON.stringify(form_data, null, 2),
                },
                success: console.log('success'),
                error: console.log('error')
            });
        }
    })
})(django.jQuery);
