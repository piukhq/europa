window.addEventListener("load", function () {
    (function ($) {
        var form_data = {};

        $('.button-primary.upload_to_vault').click(function () {
            /* The 'upload to vault' button is rendered dynamically depending on how many security credentials there are
         * so here we grab the values relative to the button that's clicked */
            $(this).css('background-color', '#EEAA33');
            // Clicked button
            var table_row = $(this).parents("tr.djn-tr.form-row");

            // Get Service type value
            var table = table_row.parents("tbody");
            var service_type = table[1].children[0].children[1].children[0].value;

            // Get Handler type value
            var handler_type = $("#id_handler_type").val();

            // Get credential type
            var credential_type = table_row.children(".field-type").children().val();

            // Get file type
            var file_input = table_row.children(".field-key_to_store").children();
            var source_file = file_input.get(0).files[0];

            console.log("service_type: " + service_type);
            console.log("handler_type: " + handler_type);
            console.log("credential_type: " + credential_type);
            console.log("source_file: " + source_file);
            console.log("reading file....");
            read_file(source_file, credential_type, service_type, handler_type);
            console.log("file read successfully.");

        });

        function read_file(source_file, credential_type, service_type, handler_type) {
            var reader = new FileReader();
            reader.onload = function (e) {
                build_dict(reader.result, credential_type, service_type, handler_type)
            };
            reader.readAsText(source_file);
        }

        function build_dict(file_contents, credential_type, service_type, handler_type) {

            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = $.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }

            form_data['csrfmiddlewaretoken'] = getCookie('csrftoken');
            form_data['merchant_id'] = $('#id_merchant_id').val();
            form_data['service_type'] = service_type;
            form_data['handler_type'] = handler_type;
            form_data['credential_type'] = credential_type;
            form_data['file'] = file_contents;

            send_data(form_data);
        }

        function send_data(form_data) {
            $.ajax({
                type: 'POST',
                url: '/config_service/form_data/',
                contentType: 'application/x-www-form-urlencoded',
                data: form_data
            });
        }
    })(django.jQuery);
});
