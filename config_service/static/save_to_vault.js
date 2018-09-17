(function($) {
    $(document).ready(function() {

        if (!$) {
            $ = django.jQuery;
        }

        var form_data = {};

        $('#upload_to_vault').click(function() {
            var file_input = $('#id_securityservice_set-0-securitycredential_set-0-key_to_store');
            var source_file = file_input.get(0).files[0];

            read_file(source_file);
        });

        function read_file(source_file){
            var reader = new FileReader();
            reader.onload = function(e){
                build_dict(reader.result)
            };
            reader.readAsText(source_file);
        }

        function build_dict(file_contents){
            form_data['merchant_id'] = $('#id_merchant_id').val();
            form_data['service_type'] = $('#id_securityservice_set-0-type').val();
            form_data['credential_type'] = $('#id_securityservice_set-0-securitycredential_set-0-type').val();
            form_data['file'] = file_contents;
            send_data(form_data)

        }

        function send_data(form_data){
            $.get({
                url: '/form_data/',
                contentType: 'application/x-www-form-urlencoded',
                data: form_data,
                success: console.log('success'),
                error: console.log('error')
            });
        }
    });

        // Check form_data has all data needed to create hash
        // function check_dict(form_data) {
        //     var count = 0;
        //     for (var data in form_data) {
        //         if (form_data.hasOwnProperty(data)) count++;
        //     }
        //
        //     if (count >= 4){
        //         send_data(form_data)
        //     } else {
        //         alert("Select Merchant ID; Security Services Request Type; Security Credentials Type")
        //     }
        // }

})(django.jQuery);
