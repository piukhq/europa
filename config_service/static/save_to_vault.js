(function($) {
    $(document).ready(function() {

        if (!$) {
            $ = django.jQuery;
        }

        var file = null;

        $('#upload_to_vault').submit(function(e){
            e.preventDefault();


            var form_data = new FormData($('#id_securityservice_set-0-securitycredential_set-0-key_to_store')[0])

            var data = new FormData();
            data = $('#id_securityservice_set-0-securitycredential_set-0-key_to_store')[0].files[0];

            // file = $('#id_securityservice_set-0-securitycredential_set-0-key_to_store')[0].files[0];
            // data.append("file", file);
            // data.append("merchant_id", $('#id_merchant_id').val());
            // data.append("service_type", $('#id_securityservice_set-0-type').val());
            // data.append("credential_type", $('#id_securityservice_set-0-securitycredential_set-0-type').val());

            // form_data['merchant_id'] = $('#id_merchant_id').val();
            // form_data['service_type'] = $('#id_securityservice_set-0-type').val();
            // form_data['credential_type'] = $('#id_securityservice_set-0-securitycredential_set-0-type').val();
            // form_data['file'] = $('#id_securityservice_set-0-securitycredential_set-0-key_to_store').get(0).files;

            send_data(data)
        });

        // Check form_data has all data needed to create hash
        function check_dict(form_data) {
            var count = 0;
            for (var data in form_data) {
                if (form_data.hasOwnProperty(data)) count++;
            }

            if (count >= 4){
                send_data(form_data)
            } else {
                alert("Select Merchant ID; Security Services Request Type; Security Credentials Type")
            }
        }

        // Ajax send data to django
        function send_data(data) {
            // $('#configuration_form').submit(function(event){
            //     event.preventDefault();
            $.ajax({
                type: "POST",
                url: '/form_data/',
                contentType: false,
                processData: false,
                data: {
                    'form_data': data,
                },
                success: console.log('success'),
                error: console.log('error')
            });

            //     $.get({
            //         url: '/form_data/',
            //         contentType: 'json',
            //         data: {
            //             'form_data': form_data
            //             // 'form_data': JSON.stringify(form_data, null, 2),
            //         },
            //         success: console.log('success'),
            //         error: console.log('error')
            //     });
            // })


            //     var form_data = {};
            //
            //     $('#id_securityservice_set-0-securitycredential_set-0-key_to_store').on('change', prepareUpload);
            //
            //     function prepareUpload() {
            //         var file = $('#id_securityservice_set-0-securitycredential_set-0-key_to_store')[0];
            //         var reader = new FileReader();
            //         reader.readAsText(file, 'UTF-8');
            //         reader.onload = send_data;
            //     }
            //
            //     // Upload to vault button is clicked
            //     $('#upload_to_vault').click(function() {
            //
            //         form_data['merchant_id'] = $('#id_merchant_id').val();
            //         form_data['service_type'] = $('#id_securityservice_set-0-type').val();
            //         form_data['credential_type'] = $('#id_securityservice_set-0-securitycredential_set-0-type').val();
            //         form_data['key_to_store'] = file.files();
            //
            //         check_dict(form_data)
            //     });
            //
            //     // Check form_data has all data needed to create hash
            //     function check_dict(form_data) {
            //         var count = 0;
            //         for (var data in form_data) {
            //             if (form_data.hasOwnProperty(data)) count++;
            //         }
            //
            //         if (count >= 3){
            //             send_data(form_data)
            //         } else {
            //             alert("Select Merchant ID; Security Services Request Type; Security Credentials Type")
            //         }
            //     }
            //
            //     // Ajax send data to django
            //     function send_data(event) {
            //         var result = event.target.result;
            //
            //         $.ajax({
            //             type: "POST",
            //             url: '/form_data/',
            //             contentType: 'json',
            //             data: {
            //                 'form_data': result
            //                 // 'form_data': JSON.stringify(form_data, null, 2),
            //             },
            //             success: console.log('success'),
            //             error: console.log('error')
            //         });
            //     }
        }})

})(django.jQuery);
