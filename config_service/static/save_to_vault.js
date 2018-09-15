(function($) {
    $(document).ready(function() {

        if (!$) {
            $ = django.jQuery;
        }

        var form_data = {};

        $('#upload_to_vault').click(function() {

            var file_input = $('#id_securityservice_set-0-securitycredential_set-0-key_to_store');

            var source_file = file_input.get(0).files[0];
            var textType = /text.*/;

            if (source_file.type.match(textType)) {
                read_file(source_file)
            } else {
                console.log("file not supported")
            }
        });

        function read_file(source_file){
            var reader = new FileReader();
            reader.readAsText(source_file);
            return reader.result
        }

        function build_dict(source_file){
            form_data['merchant_id'] = $('#id_merchant_id').val();
            form_data['service_type'] = $('#id_securityservice_set-0-type').val();
            form_data['credential_type'] = $('#id_securityservice_set-0-securitycredential_set-0-type').val();
            form_data['file'] = reader.result;
            return form_data

        }

        function send_data(build_dict){
            $.get({
                url: '/form_data/',
                contentType: false,
                async: false,
                data: {
                    'form_data': form_data,
                },
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
