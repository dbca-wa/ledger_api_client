var system_ledger_management = {
	var:{
            config: {},
              
    },
    init: function (system_id) {
        system_ledger_management.load_personal_details();
        system_ledger_management.load_contact_details();
        system_ledger_management.load_address_details();

        var html = '';
        var ledger_ui_card_details = $('#ledger_ui_card_details').length;
        if (ledger_ui_card_details > 0) {                        
                html += "<div id='div-ledger-ui-card-details-loader'>"+ledger_management.var.pagesettings.loader+"</div>";
                html += "<div id='div-ledger-ui-card-details' class='row mx-md-n5 border p-2 ms-3 me-3 mb-3' style='display:none'>";
                html += "<div ><div class='col-12 text-end'><button class='btn btn-sm btn-primary m-1' id='primary-card-button'>Primary Card</button><button class='btn btn-sm btn-primary m-1' id='add-card-button'>Add Card</button></a></div></div>";
                html += "<div class='col-12' id='div-ledger-ui-list-card-details'></div>";
                html += "</div>";
                $('#ledger_ui_card_details').html(html);

                ledger_management.cards.get_card_data();
                ledger_management.cards.display_cards();

                $("#add-card-button").click(function() {
                    $('#ledger_ui_add_card_message').html('');
                    $('#id_number').val('');
                    $('#id_expiry_month_0').val('');
                    $('#id_expiry_month_1').val('');
                    $('#id_ccv').val('');                            
                    $('#AddNewCardModal').modal('show');
                });

                $("#save-card-button").click(function() {
                    ledger_management.cards.save_card();
                });

                $("#save_card_loader").hide();
                $("#save_card_loader").html(ledger_management.var.pagesettings.button_loader);
                $("#save_primary_card_loader").hide();
                $("#save_primary_card_loader").html(ledger_management.var.pagesettings.button_loader);
                save_primary_card_loader
                $("#primary-card-button").click(function() {
                    ledger_management.cards.primary_display_cards();
                    $('#PrimaryCardModal').modal('show');
                });

                $("#save-primary-card-button").click(function() {
                    $("input[name=primary-card]").prop( "disabled", false );
                    ledger_management.cards.save_primary_card();
                });

                $('#delete_card_confirm_btn').click(function() {
                      var delete_card_id = $('#delete_card_id').val();
                      ledger_management.cards.delete_card(delete_card_id);
                      $('#DeleteCardConfirmModal').modal('hide');
                });            
            }


            $('#nav-cards-tab-page').hide();
            $('.managed-account-nav').click(function() {
                $('.managed-account-nav').each(function(i, obj) {                               
                    $("#"+obj.id+'-page').hide();
                });
                $("#"+this.id+'-page').show();                          
            });


    },
    load_personal_details: function(data) {
        $.ajax({
            url: '/ledger-ui/crispy-form/account-information/'+system_ledger_management.var.system_user_id+'/',
            method: "GET",                        
            contentType: "text/html",
            success: function(data) {
                
                $('#ledger_ui_account_details').html(data);                            
            },
            error: function (error) {
                console.log('Error updating account information');
                if (error.status == 403 || error.status == 401) { 
                    $('#id_create_edit_address_information').html('<div class="alert alert-danger" >ERROR: Your do not have permissions to access this resource or your session has expired.</div>');
                } else {
                    $('#id_create_edit_address_information').html('<div class="alert alert-danger" >ERROR: Unknown error occured while processing your request.</div>');
                }
            },
        });


        $.ajax({
            url: '/ledger-ui/crispy-form/personal-information/'+system_ledger_management.var.system_user_id+'/',
            method: "GET",
            // headers: {'X-CSRFToken' : ledger_management.var.csrf_token},
            // data: JSON.stringify({'payload': data,}),
            contentType: "text/html",
            success: function(data) {
                
                $('#ledger_ui_personal_details').html(data);
                $('#id_personal_information_btn').click(function() {
                    
                })
                console.log('Success');
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
    },
    load_contact_details: function(data) {
        $.ajax({
            url: '/ledger-ui/crispy-form/contact-information/'+system_ledger_management.var.system_user_id+'/',
            method: "GET",
            // headers: {'X-CSRFToken' : ledger_management.var.csrf_token},
            // data: JSON.stringify({'payload': data,}),
            contentType: "text/html",
            success: function(data) {
                
                $('#ledger_ui_contact_details').html(data);
                $('#id_contact_information_btn').click(function() {
                   
                })
                console.log('Success');
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
    },
    load_address_details: function(data) {
        $.ajax({
            url: '/ledger-ui/crispy-form/address-information/'+system_ledger_management.var.system_user_id+'/',
            method: "GET",
            // headers: {'X-CSRFToken' : ledger_management.var.csrf_token},
            // data: JSON.stringify({'payload': data,}),
            contentType: "text/html",
            success: function(data) {
                
                $('#ledger_ui_address_details').html(data);

                console.log('Success');
            },
            error: function (error) {
                if (error.status == 403 || error.status == 401) { 
                    $('#id_create_edit_address_information').html('<div class="alert alert-danger" >ERROR: Your do not have permissions to access this resource or your session has expired.</div>');
                } else {
                    $('#id_create_edit_address_information').html('<div class="alert alert-danger" >ERROR: Unknown error occured while processing your request.</div>');
                }
                console.log('Error updating address information');
            },
        });
    },
    load_address_create: function(data) {
        $.ajax({
            url: '/ledger-ui/crispy-form/address-information/'+system_ledger_management.var.system_user_id+'/create',
            method: "GET",
            // headers: {'X-CSRFToken' : ledger_management.var.csrf_token},
            // data: JSON.stringify({'payload': data,}),
            contentType: "text/html",
            success: function(data) {
                
                $('#id_create_edit_address_information').html(data);

                console.log('Success');
            },
            error: function (error) {
                if (error.status == 403 || error.status == 401) { 
                    $('#id_create_edit_address_information').html('<div class="alert alert-danger" >ERROR: Your do not have permissions to access this resource or your session has expired.</div>');
                } else {
                    $('#id_create_edit_address_information').html('<div class="alert alert-danger" >ERROR: Unknown error occured while processing your request.</div>');
                }
                console.log('Error creating address information');
            },
        });
    },
    load_address_edit: function(address_id) {
        $.ajax({
            url: '/ledger-ui/crispy-form/address-information/'+system_ledger_management.var.system_user_id+'/edit/'+address_id,
            method: "GET",
            contentType: "text/html",
            success: function(data) {                
                $('#id_create_edit_address_information').html(data);
                console.log('Success');
            },
            error: function (error) {
                if (error.status == 403 || error.status == 401) { 
                    $('#id_create_edit_address_information').html('<div class="alert alert-danger" >ERROR: Your do not have permissions to access this resource or your session has expired.</div>');
                } else {
                    $('#id_create_edit_address_information').html('<div class="alert alert-danger" >ERROR: Unknown error occured while processing your request.</div>');
                }
                 console.log('Error updating address information');
            },
        });
    },
    load_address_delete: function(address_id) {
        $.ajax({
            url: '/ledger-ui/crispy-form/address-information/'+system_ledger_management.var.system_user_id+'/delete/'+address_id,
            method: "GET",
            contentType: "text/html",
            success: function(data) {                
                $('#id_create_edit_address_information').html(data);
                console.log('Success');
            },
            error: function (error) {
                if (error.status == 403 || error.status == 401) { 
                    $('#id_create_edit_address_information').html('<div class="alert alert-danger" >ERROR: Your do not have permissions to access this resource or your session has expired.</div>');
                } else {
                    $('#id_create_edit_address_information').html('<div class="alert alert-danger" >ERROR: Unknown error occured while processing your request.</div>');
                }
                 console.log('Error updating address information');
            },
        });
    }          



    
}
    