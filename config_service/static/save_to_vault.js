(function($) {
    $(document).ready(function() {

        if (!$) {
            $ = django.jQuery;
        }

        var form_data = {};

        $('.button-primary.upload_to_vault').click(function() {

            /* The 'upload to vault' button is rendered dynamically depending on how many security credentials there are
         * so here we grab the values relative to the button that's clicked */

            // Clicked button
            var table_row = $(this).parents("tr.djn-tr.form-row");

            // Get Service type value
            var table = table_row.parents("tbody");
            var service_type = table[1].children[0].children[1].children[0].value;

            // Get credential type
            var credential_type = table_row.children(".field-type").children().val();

            // Get file type
            var file_input = table_row.children(".field-key_to_store").children();
            var source_file = file_input.get(0).files[0];
            read_file(source_file, credential_type, service_type);

        });

        function read_file(source_file, credential_type, service_type){
            var reader = new FileReader();
            reader.onload = function(e){
                build_dict(reader.result, credential_type, service_type)
            };
            reader.readAsText(source_file);
        }

        function build_dict(file_contents, credential_type, service_type){
            form_data['merchant_id'] = $('#id_merchant_id').val();
            form_data['service_type'] = service_type;
            form_data['credential_type'] = credential_type;
            form_data['file'] = file_contents;
            send_data(form_data);
        }

        // function check_dict(form_data) {
        //     var count = 0;
        //     for (var data in form_data) {
        //         if (form_data.hasOwnProperty(data)) count++;
        //     }
        //     if (count >= 4){
        //         send_data(form_data)
        //     } else {
        //         alert("Select Merchant ID; Security Services Request Type; Security Credentials Type and choose a file")
        //     }
        // }

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

})(django.jQuery);
