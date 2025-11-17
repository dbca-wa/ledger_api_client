var ledger_api_django_crispy_forms = {
    submit_form: function(form_id, parent_div) { 
        $("#"+form_id).each(function(){
            var form_obj = this;
            var form_url = this.action;
            var form_method = this.method;
            var form_payload = {};
            var form_id = this.id;
            var csrf_token = csrf_token;
            console.log("FORMID"+form_id);
            var form_element = $("input, textarea, select", this);
            form_element.each(function(){
                // console.log(this.name);
                // console.log(this.value);
                // console.log(this.id);   

                if (this.type == 'checkbox') {                     
                    form_payload[this.name]  = $(this).prop('checked');
                } else {
                    form_payload[this.name]  = this.value;
                }
                if (this.name == 'csrfmiddlewaretoken') {
                    csrf_token = this.name;

                }
            })
            console.log(form_payload);

            // $('#'+parent_div).prepend('<div class="col-12 text-center pt-3"><div class="spinner-border" style="width: 3rem; height: 3rem;" role="status"><span class="visually-hidden">Loading...</span></div></div>');            

            $('#'+parent_div).prepend('<div class="col-12 text-center pt-3"><button class="btn btn-warning" type="button" disabled><span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving Please Wait...</button></div><BR>');
            $("#"+parent_div).each(function(){
                let $inputs = $("input, textarea, select, button", this);
                $inputs.prop("disabled", true);
            });
            $.ajax({
                url: form_url,
                type: 'POST',
                headers: {'X-CSRFToken' : csrf_token},
                data: form_payload,            
                success: function(data,textStatus,xhr) {
                    
                    console.log('Success');
                    if (xhr.status == 302) { 
                       console.log(console.log(xhr.responseURL))
                       console.log("UPDATE SUCCESS");
                    } else if (xhr.status == 200) {
                        $("#"+parent_div).html(data);                
                    } else {
                        $("#"+parent_div).html("UKNOWN ERROR LOADING.");
                        // var scripttags = data.match(/<script\b[^>]*>[\s\S]*?<\/script\b[^>]*>/g);
                                                
                        // for (var i = 0; i < scripttags.length; ++i) {
                        //   var script = scripts[i];
                        //   var scripttags_cleaned = script.replace(/['"]+|<script |><\/script>|<\/script>/g, '').split(' ')
                        //   console.log(scripttags_cleaned);
                        //   //eval(script.innerHTML);
                        // }                                                
                    }
                },
                error: function (error) {
                    if (error.status == 403 || error.status == 401) { 
                        $('#id_create_edit_address_information').html('<div class="alert alert-danger" >ERROR: Your do not have permissions to access this resource or your session has expired.</div>');
                    } else {
                        $('#id_create_edit_address_information').html('<div class="alert alert-danger" >ERROR: Unknown error occured while processing your request.</div>');
                    }                                        
                    console.log('Error updating account information');
                },
            });


        });
     

    }

}