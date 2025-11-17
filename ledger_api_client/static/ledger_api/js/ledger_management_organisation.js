var ledger_management_organisation = {
	var: {
            config: {},
            config_status:{},
            data:  {organisation: {org_id: null}},
            information_status: {
                'organisation_details_completed': false,
                'address_details_completed' : false,
                'contact_details_completed' : false
            },
            countries: [],
            countries_status:{},
            organisation_data: {},
            organisation_data_status:{},
            address: {},
            identification: {},
            contact: {},
            is_loading: false,
            csrf_token: '',
            primary_card_id: -1,
            pagesettings: {
                    loader: "<div class='text-center p-5'><div class='spinner-grow text-primary' role='status'><span class='visually-hidden'>Loading...</span></div><div class='fw-bold'>Loading</div></div>",
                    button_loader: "<button class='btn btn-primary' type='button' disabled><span class='spinner-grow spinner-grow-sm' role='status'></span>&nbsp;&nbsp;Loading...</button>"
            },
    },
    get_countries: function() {
        ledger_management_organisation.var.is_loading = true;
        $.ajax({
            url: '/ledger-ui/api/get-countries/',
            method: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            //data: "{}",
            success: function(response) {
                 ledger_management_organisation.var.countries = response.data;
                 ledger_management_organisation.var.countries_status.is_loading = false;
                 ledger_management_organisation.var.countries_status.loading = false;
                 ledger_management_organisation.var.countries_status.completed = true;                
            },
            error: function(error) {
                //ledger_management_organisation.var.countries = response.data;
                ledger_management_organisation.var.countries_status.is_loading = false;
                ledger_management_organisation.var.countries_status.loading = false;
                ledger_management_organisation.var.countries_status.completed = true;                         
                console.log('Error loading get countries');
            },
        });
    },
    get_settings: function() {
        ledger_management_organisation.var.config_status.is_loading = true;
        $.ajax({
            url: '/ledger-ui/api/get-organisation-settings/',
            method: 'GET',
            dataType: 'json',
            cache: false,
            contentType: 'application/json',
            //data: "{}",
            success: function(response) {
                for (let i = 0; i < response.config.length; i++) {
                    key = Object.keys(response.config[i]);
                    ledger_management_organisation.var.config[key[0]] = response.config[i][key[0]];
                }
                ledger_management_organisation.var.config_status.is_loading = false;
            },
            error: function(error) {
                ledger_management_organisation.var.config_status.is_loading = false;
                console.log('Error loading get settings');
            },
        });
    },
    init: function (org_id) {
        ledger_management_organisation.var.csrf_token = $('#ledger_ui_csrf_token').val();
        ledger_management_organisation.var.data.organisation.org_id = org_id;     
        ledger_management_organisation.get_settings();
        ledger_management_organisation.init_begin(org_id);    
        
        $('.managed-organisation-nav').click(function() {
            $('.managed-organisation-nav').each(function(i, obj) {  
                console.log(obj.id);                         
                $("#"+obj.id+'-page').hide();
            });
            $("#"+this.id+'-page').show();                          
        });    
    },
    init_begin: function (org_id) {

        if (ledger_management_organisation.var.config_status.is_loading == false) { 
            console.log("settings loaded")
            ledger_management_organisation.organisation.init();
            ledger_management_organisation.address.init();
        } else {
            setTimeout("ledger_management_organisation.init_begin("+org_id+");", 200);
        }     

    },
	update_organisation_details: function(data) {
        ledger_management_organisation.var.organisation_data_status.is_loading = true;
                var data = data;
                $.ajax({
                    url: '/ledger-ui/api/update-organisation-details/'+ledger_management_organisation.var.data.organisation.org_id+'/',
                    method: "POST",
                    headers: {'X-CSRFToken' : ledger_management_organisation.var.csrf_token},
                    data: JSON.stringify({'payload': data,}),
                    contentType: "application/json",
                    success: function(data) {
                        ledger_management_organisation.var.organisation_data_status.is_loading = false;
                        ledger_management_organisation.get_organisation_details();

                        console.log('Success');
                    },
                    error: function (error) {
                        ledger_management_organisation.var.organisation_data_status.is_loading = false;
                        ledger_management_organisation.get_organisation_details();
                        
                        console.log('Error updating organisation information');
                        alert("Error updating organisation information");
                    },
                });
       },
    get_organisation_details: function() {
        ledger_management_organisation.var.organisation_data_status.is_loading = true;
        $.ajax({
            url: '/ledger-ui/api/get-organisation-details/'+ledger_management_organisation.var.data.organisation.org_id+'/',
            method: 'GET',
            dataType: 'json',
            cache: false,
            contentType: 'application/json',         
            success: function(response) {                
                //  for (let i = 0; i < response.config.length; i++) {
                //      key = Object.keys(response.config[i]);
                //      ledger_management_organisation.var.config[key[0]] = response.config[i][key[0]];
                //  }
                ledger_management_organisation.var.organisation_data = response.data;
                ledger_management_organisation.var.organisation_data_status.is_loading = false;
                ledger_management_organisation.var.organisation_data_status.loading = false;
                ledger_management_organisation.var.organisation_data_status.completed = true;
                ledger_management_organisation.var.organisation_data_status.information_status = response.information_status;

            },
            error: function(error) {
                
                ledger_management_organisation.var.organisation_data_status.is_loading = false;
                ledger_management_organisation.var.organisation_data_status.loading = false;
                ledger_management_organisation.var.organisation_data_status.completed = true;  
                ledger_management_organisation.var.organisation_data_status.information_status = response.information_status;                              
                console.log('Error loading organisation details');
            },
        });
    },
    organisation : {
        update_data: function() {
            $('#div-ledger-ui-organisation').hide();
            $('#div-ledger-ui-organisation-loader').show();
            var data = {};
            var organisation_name = $('#input-ledger-ui-organisation-name');
            var organisation_abn = $('#input-ledger-ui-organisation-abn');
            data['organisation_name'] = organisation_name.val();
            // data['organisation_abn'] = organisation_abn.val();
            console.log(data);            
            ledger_management_organisation.update_organisation_details(data);
            ledger_management_organisation.organisation.get_data_loading();
        },
        get_data: function() {
         
            $('#input-ledger-ui-organisation-name').val(ledger_management_organisation.var.organisation_data.data.organisation_name);
            $('#input-ledger-ui-organisation-abn').val(ledger_management_organisation.var.organisation_data.data.organisation_abn);

            $('#div-ledger-ui-organisation-loader').hide();
            $('#div-ledger-ui-organisation').show();  
            
            if (ledger_management_organisation.var.organisation_data.data.organisation_name.length > 2) { 
                $('#organisation-details-status').html('<i class="bi bi-check-circle-fill" style="color: #08c508;"></i>');

            } else {
                $('#organisation-details-status').html('<i class="bi bi-x-circle-fill" style="color: #ff0909"></i>');
            }            
        },
        get_data_loading: function() {
            $('#div-ledger-ui-organisation').hide();
            $('#div-ledger-ui-organisation-loader').show();
            

            if (ledger_management_organisation.var.organisation_data_status.is_loading == false) { 
                console.log("completed")
                ledger_management_organisation.organisation.get_data();
            } else {
                setTimeout("ledger_management_organisation.organisation.get_data_loading();", 200);
            }            
            
        },
        init: function() {
           
            $('#ledger_ui_organisation_details').html(ledger_management_organisation.var.pagesettings.loader);

            var html = "";
            html += "<div id='div-ledger-ui-organisation-loader'>"+ledger_management_organisation.var.pagesettings.loader+"</div>";
            html += "<div id='div-ledger-ui-organisation' style='display:none'>";

            html += "<div class='row mx-md-n5'>";
            if ('organisation_name' in ledger_management_organisation.var.config) {
                html += "       <div class='col-3 text-end p-2'>";
                html += "         <label for='inputLine1' class='col-form-label fw-bold'>Name</label>";
                html += "       </div>";
                html += "       <div class='col-5 p-2'> ";
                html += "         <input type='input' id='input-ledger-ui-organisation-name' class='form-control' autocomplete='off'>";
                html += "       </div>";
                html += "       <div class='col-4  p-2'>";
                html += "           <span id='moreinfoInline' class='form-text'>";
                html += "             ";
                html += "         </span>";
                html += "       </div>";
            }
            if ('organisation_abn' in ledger_management_organisation.var.config) {
                html += "       <div class='col-3 text-end p-2'>";
                html += "         <label for='inputLine1' class='col-form-label fw-bold'>ABN</label>";
                html += "       </div>";
                html += "       <div class='col-5 p-2'> ";
                html += "         <input type='input' id='input-ledger-ui-organisation-abn' class='form-control' autocomplete='off' disabled=true>";
                html += "       </div>";
                html += "       <div class='col-4  p-2'>";
                html += "           <span id='moreinfoInline' class='form-text'>";
                html += "             ";
                html += "         </span>";
                html += "       </div>";
            }

            html += " <div class='d-grid gap-2 d-md-flex justify-content-md-end'> <button class='pull-right btn btn-primary' id='update-organisation-details'>Update</button></div>";
            html += "</div>";
            html += "</div>";
             
            $('#ledger_ui_organisation_details').html(html);

            ledger_management_organisation.get_organisation_details();            
            ledger_management_organisation.organisation.get_data_loading();
            
            $('#update-organisation-details').click(function() {
                    ledger_management_organisation.organisation.update_data();
            });
       }



    },
    address:{

        update_data_billing: function() {
            $('#div-ledger-ui-billing-address').hide();
            $('#div-ledger-ui-billing-address-loader').show();

            // $('#div-ledger-ui-postal-address').hide();
            // $('#div-ledger-ui-postal-address-loader').show();

            var data = {"billing_address": {}};
            var billing_line1 = $('#input-ledger-ui-billing-address-line1');
            var billing_locality = $('#input-ledger-ui-billing-address-locality');
            var billing_state = $('#input-ledger-ui-billing-address-state');
            var billing_postcode = $('#input-ledger-ui-billing-address-postcode');
            var billing_country = $('#input-ledger-ui-billing-address-country');
            
            data['billing_address']['billing_line1'] = billing_line1.val();
            data['billing_address']['billing_locality'] = billing_locality.val();
            data['billing_address']['billing_state'] = billing_state.val();
            data['billing_address']['billing_postcode'] = billing_postcode.val();
            data['billing_address']['billing_country'] = billing_country.val();

            ledger_management_organisation.update_organisation_details(data);
            ledger_management_organisation.address.get_data_loading();

        },


        update_data_postal: function() {
            $('#div-ledger-ui-postal-address').hide();
            $('#div-ledger-ui-postal-address-loader').show();

            // $('#div-ledger-ui-postal-address').hide();
            // $('#div-ledger-ui-postal-address-loader').show();

            var data = {"postal_address": {}};
            var postal_line1 = $('#input-ledger-ui-postal-address-line1');
            var postal_locality = $('#input-ledger-ui-postal-address-locality');
            var postal_state = $('#input-ledger-ui-postal-address-state');
            var postal_postcode = $('#input-ledger-ui-postal-address-postcode');
            var postal_country = $('#input-ledger-ui-postal-address-country');
            
            data['postal_address']['postal_line1'] = postal_line1.val();
            data['postal_address']['postal_locality'] = postal_locality.val();
            data['postal_address']['postal_state'] = postal_state.val();
            data['postal_address']['postal_postcode'] = postal_postcode.val();
            data['postal_address']['postal_country'] = postal_country.val();

            ledger_management_organisation.update_organisation_details(data);
            ledger_management_organisation.address.get_data_loading();
        },

        get_data: function() {
            $('#div-ledger-ui-billing-address').show();
            $('#div-ledger-ui-billing-address-loader').hide();
            $('#div-ledger-ui-postal-address').show();
            $('#div-ledger-ui-postal-address-loader').hide();

            var countries_select_html ="";
            for (let i = 0; i < ledger_management_organisation.var.countries.length; i++) {
                countries_select_html += "<option value='"+ledger_management_organisation.var.countries[i].country_code+"'>"+ledger_management_organisation.var.countries[i].country_name+"</option>"; 
            }
            $('#input-ledger-ui-billing-address-country').html(countries_select_html);
            $('#input-ledger-ui-postal-address-country').html(countries_select_html);
            // if ('residential_address' in ledger_management_organisation.var.config) {
                    //if ('residential_line1' in ledger_management.var.config ) {
                        $('#input-ledger-ui-billing-address-line1').val(ledger_management_organisation.var.organisation_data.data.billing_address.line1); 
                    //}
                    //if ('residential_locality' in ledger_management.var.config ) {
                        $('#input-ledger-ui-billing-address-locality').val(ledger_management_organisation.var.organisation_data.data.billing_address.locality);
                    //}
                    //if ('residential_state' in ledger_management.var.config ) {
                        $('#input-ledger-ui-billing-address-state').val(ledger_management_organisation.var.organisation_data.data.billing_address.state);
                    //}
                    //if ('residential_postcode' in ledger_management.var.config ) {
                        $('#input-ledger-ui-billing-address-postcode').val(ledger_management_organisation.var.organisation_data.data.billing_address.postcode);
                    //}
                    //if ('residential_country' in ledger_management.var.config ) {
                        $('#input-ledger-ui-billing-address-country').val(ledger_management_organisation.var.organisation_data.data.billing_address.country);
                    //}
            // }


            $('#input-ledger-ui-postal-address-line1').val(ledger_management_organisation.var.organisation_data.data.postal_address.line1);
		    
            $('#input-ledger-ui-postal-address-locality').val(ledger_management_organisation.var.organisation_data.data.postal_address.locality);
		    
            $('#input-ledger-ui-postal-address-state').val(ledger_management_organisation.var.organisation_data.data.postal_address.state);
            
            $('#input-ledger-ui-postal-address-postcode').val(ledger_management_organisation.var.organisation_data.data.postal_address.postcode);
            
            $('#input-ledger-ui-postal-address-country').val(ledger_management_organisation.var.organisation_data.data.postal_address.country);                    

            var address_status = false;
            var billing_address_status = false;
            var postal_address_status = false;
             


            if (ledger_management_organisation.var.organisation_data.data.billing_address.line1.length > 2 && 
                ledger_management_organisation.var.organisation_data.data.billing_address.locality.length > 2 &&
                ledger_management_organisation.var.organisation_data.data.billing_address.state.length > 1 &&
                ledger_management_organisation.var.organisation_data.data.billing_address.postcode.length > 1 &&
                ledger_management_organisation.var.organisation_data.data.billing_address.country.length > 1) {

                    billing_address_status = true;

                }

            if (ledger_management_organisation.var.organisation_data.data.postal_address.line1.length > 2 && 
                ledger_management_organisation.var.organisation_data.data.postal_address.locality.length > 2 &&
                ledger_management_organisation.var.organisation_data.data.postal_address.state.length > 1 &&
                ledger_management_organisation.var.organisation_data.data.postal_address.postcode.length > 1 &&
                ledger_management_organisation.var.organisation_data.data.postal_address.country.length > 1

               )            { 
                postal_address_status = true;

               }


            if ('postal_address' in ledger_management_organisation.var.config && 'billing_address' in ledger_management_organisation.var.config) {
                if (billing_address_status == true && postal_address_status == true) {
                    address_status = true
                }
            } else {

            if ('billing_address' in ledger_management_organisation.var.config) {
                if (billing_address_status == true) {
                    address_status = true
                }

            }

            if ('postal_address' in ledger_management_organisation.var.config) {
                if (postal_address_status == true) {
                    address_status = true
                }

            }


            }



            if (address_status == true) { 
                $('#address-details-status').html('<i class="bi bi-check-circle-fill" style="color: #08c508;"></i>');

            } else {
                $('#address-details-status').html('<i class="bi bi-x-circle-fill" style="color: #ff0909"></i>');
            }  


        },
        get_data_loading: function() {
            // $('#div-ledger-ui-billing-address').hide();
            // $('#div-ledger-ui-billing-address-loader').show();
            // $('#div-ledger-ui-postal-address').hide();
            // $('#div-ledger-ui-postal-address-loader').show();

            

            if (ledger_management_organisation.var.organisation_data_status.is_loading == false) { 
                ledger_management_organisation.address.get_data();
            } else {
               setTimeout("ledger_management_organisation.address.get_data_loading();", 500);
            }
        },

        init: function() {
            //$('#ledger_ui_residential_details').html(ledger_management.var.pagesettings.loader);
            // Postal
            var html = "";

            if ('billing_address' in ledger_management_organisation.var.config) {
                html += "<div id='div-ledger-ui-billing-address-loader'>"+ledger_management_organisation.var.pagesettings.loader+"</div>";
                html += "<div id='div-ledger-ui-billing-address' style='display:none'>";

                html += "<div class='ms-3 mb-1 me-3'><h6>Billing Address</h6></div>";
                html += "<div class='row mx-md-n5 border p-2 ms-3 me-3 mb-3'>";
                html += "       <div class='col-3 text-end p-2'>";
                html += "         <label for='inputLine1' class='col-form-label fw-bold'>Address</label>";
                html += "       </div>";
                html += "       <div class='col-5 p-2'> ";
                html += "         <input type='input' id='input-ledger-ui-billing-address-line1' class='form-control' autocomplete='off'>";
                html += "       </div>";
                html += "       <div class='col-4  p-2'>";
                html += "           <span id='moreinfoInline' class='form-text'>";
                html += "             ";
                html += "         </span>";
                html += "       </div>";

                html += "       <div class='col-3 text-end p-2'>";
                html += "         <label for='inputLine2' class='col-form-label fw-bold'>Town/Suburb</label>";
                html += "       </div>";
                html += "       <div class='col-5 p-2'>";
                html += "         <input type='input' id='input-ledger-ui-billing-address-locality' class='form-control' autocomplete='off'>";
                html += "       </div>";
                html += "       <div class='col-4 p-2'>";
                html += "         <span id='lineInline' class='form-text'>";
                html += "         </span>";
                html += "       </div>";

                html += "       <div class='col-3 text-end p-2'>";
                html += "         <label for='inputLine2' class='col-form-label fw-bold'>State</label>";
                html += "       </div>";
                html += "       <div class='col-5 p-2'>";
                html += "         <input type='input' id='input-ledger-ui-billing-address-state' class='form-control' autocomplete='off'>";
                html += "       </div>";
                html += "       <div class='col-4 p-2'>";
                html += "         <span id='lineInline' class='form-text'>";
                html += "         </span>";
                html += "       </div>";

                html += "       <div class='col-3 text-end p-2'>";
                html += "         <label for='inputLine2' class='col-form-label fw-bold'>Postcode</label>";
                html += "       </div>";
                html += "       <div class='col-5 p-2'>";
                html += "         <input type='input' id='input-ledger-ui-billing-address-postcode' class='form-control' autocomplete='off'>";
                html += "       </div>";
                html += "       <div class='col-4 p-2'>";
                html += "         <span id='lineInline' class='form-text'>";
                html += "         </span>";
                html += "       </div>";

                html += "       <div class='col-3 text-end p-2'>";
                html += "         <label for='inputLine2' class='col-form-label fw-bold'>Country</label>";
                html += "       </div>";
                html += "       <div class='col-5 p-2'>";
                html += "        <select class='form-select' id='input-ledger-ui-billing-address-country'></select>";
                //html += "         <input type='input' id='input-ledger-ui-residential-address-country' class='form-control' autocomplete='off'>";
                html += "       </div>";
                html += "       <div class='col-4 p-2'>";
                html += "         <span id='lineInline' class='form-text'>";
                html += "         </span>";
                html += "       </div>";
                html += " <div class='d-grid gap-2 d-md-flex justify-content-md-end'> <button class='pull-right btn btn-primary' id='update-billing-details'>Update</button></div>";
                html += "</div>";
                html += "</div>";

                $('#ledger_ui_billing_details').html(html);
                $('#update-billing-details').click(function() {
                    ledger_management_organisation.address.update_data_billing();
               });    
              
            }
            

            if ('postal_address' in ledger_management_organisation.var.config) {
            // Postal  ledger_ui_postal_details"
            var html = "";
            html += "<div id='div-ledger-ui-postal-address-loader'>"+ledger_management_organisation.var.pagesettings.loader+"</div>";
            html += "<div id='div-ledger-ui-postal-address' style='display:none'>";

            html += "<div class='ms-3 mb-1 me-3'><h6>Postal Address</h6></div>";
            html += "<div class='row mx-md-n5 border p-2 ms-3 me-3 mb-3'>";
            html += "       <div class='col-3 text-end p-2'>";
            html += "       ";
            html += "       </div>";
            html += "       <div class='col-5 p-2'>";
            html += "       <div style='display:none' id='div-ledger-ui-postal-address-same-as-residential'> ";
            html += "        <input class='form-check-input' type='checkbox' value='' id='input-ledger-ui-postal-address-same-as-residential' >";                    
            html += "        <label class='form-check-label'>Same as residential address</label>";
            html += "       </div>";

            html += "       </div>";
            html += "       <div class='col-4  p-2'>";
            html += "           <span id='moreinfoInline' class='form-text'>";
            html += "             ";
            html += "         </span>";
            html += "       </div>";

            
            html += "       <div class='col-3 text-end p-2'>";
            html += "         <label for='inputLine1' class='col-form-label fw-bold'>Address</label>";
            html += "       </div>";
            html += "       <div class='col-5 p-2'> ";
            html += "         <input type='input' id='input-ledger-ui-postal-address-line1' class='form-control' autocomplete='off'>";
            html += "       </div>";
            html += "       <div class='col-4  p-2'>";
            html += "           <span id='moreinfoInline' class='form-text'>";
            html += "             ";
            html += "         </span>";
            html += "       </div>";

            html += "       <div class='col-3 text-end p-2'>";
            html += "         <label for='inputLine2' class='col-form-label fw-bold'>Town/Suburb</label>";
            html += "       </div>";
            html += "       <div class='col-5 p-2'>";
            html += "         <input type='input' id='input-ledger-ui-postal-address-locality' class='form-control' autocomplete='off'>";
            html += "       </div>";
            html += "       <div class='col-4 p-2'>";
            html += "         <span id='lineInline' class='form-text'>";
            html += "         </span>";
            html += "       </div>";

            html += "       <div class='col-3 text-end p-2'>";
            html += "         <label for='inputLine2' class='col-form-label fw-bold'>State</label>";
            html += "       </div>";
            html += "       <div class='col-5 p-2'>";
            html += "         <input type='input' id='input-ledger-ui-postal-address-state' class='form-control' autocomplete='off'>";
            html += "       </div>";
            html += "       <div class='col-4 p-2'>";
            html += "         <span id='lineInline' class='form-text'>";
            html += "         </span>";
            html += "       </div>";

            html += "       <div class='col-3 text-end p-2'>";
            html += "         <label for='inputLine2' class='col-form-label fw-bold'>Postcode</label>";
            html += "       </div>";
            html += "       <div class='col-5 p-2'>";
            html += "         <input type='input' id='input-ledger-ui-postal-address-postcode' class='form-control' autocomplete='off'>";
            html += "       </div>";
            html += "       <div class='col-4 p-2'>";
            html += "         <span id='lineInline' class='form-text'>";
            html += "         </span>";
            html += "       </div>";

            html += "       <div class='col-3 text-end p-2'>";
            html += "         <label for='inputLine2' class='col-form-label fw-bold'>Country</label>";
            html += "       </div>";
            html += "       <div class='col-5 p-2'>";
            html += "        <select class='form-select' id='input-ledger-ui-postal-address-country'></select>";
            //html += "         <input type='input' id='input-ledger-ui-postal-address-country' class='form-control' autocomplete='off'>";
            html += "       </div>";
            html += "       <div class='col-4 p-2'>";
            html += "         <span id='lineInline' class='form-text'>";
            html += "         </span>";
            html += "       </div>";

            html += " <div class='d-grid gap-2 d-md-flex justify-content-md-end'> <button class='pull-right btn btn-primary' id='update-postal-details'>Update</button></div>";
            html += "</div>";
            html += "</div>";

            $('#ledger_ui_postal_details').html(html);
            $('#update-postal-details').click(function() {
                ledger_management_organisation.address.update_data_postal();
            });   
            }

            ledger_management_organisation.get_organisation_details();
            ledger_management_organisation.get_countries();

            ledger_management_organisation.address.get_data_loading();


            

        }

    }


    

}
