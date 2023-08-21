var ledger_management = {
	var: {
                config: {},
		        data:  {accounts: {user_id: null, org_id: null}},
                information_status: {
                    'address_details_completed': false,
                    'contact_details_completed' : false,
                    'personal_details_completed' : false
                },
                countries: [],
                account_data: {},
	            address: {},
		        identification: {},
		        contact: {},
                is_loading: false,
		        csrf_token: '',
                steps:  {step1: {completed: false, loading: false, exec: function() {
			                ledger_management.init_load_order.step1();
			            }}, 
                 	    step2: {completed: false,  loading: false, exec: function() {
				            ledger_management.init_load_order.step2();
				        }}, 
                        step3: {completed: false, loading: false, exec: function() {
				            ledger_management.init_load_order.step3();
				        }},
                        step4: {completed: false, loading: false, exec: function() {
                            ledger_management.init_load_order.step4();
                        }},
                        step5: {completed: false, loading: false, exec: function() {
                            ledger_management.init_load_order.step5();
                        }},                    
				},
                cards: [],
                primary_card_id: -1,
                pagesettings: {
                     loader: "<div class='text-center p-5'><div class='spinner-grow text-primary' role='status'><span class='visually-hidden'>Loading...</span></div><div class='fw-bold'>Loading</div></div>",
                     button_loader: "<button class='btn btn-primary' type='button' disabled><span class='spinner-grow spinner-grow-sm' role='status'></span>&nbsp;&nbsp;Loading...</button>"
                }
        },
        init: function (user_id) {
	    ledger_management.var.data.accounts.user_id = user_id;
	    ledger_management.init_begin();
  
        },
        init_begin: function() {
            var load_steps = Object.keys(ledger_management.var.steps);   
            var pending_steps_count = 0;
            var running_step_count = 0;
            for (let i = 0; i < load_steps.length; i++) {
                console.log(load_steps[i]);
                if (ledger_management.var.steps[load_steps[i]].completed == false) { 
                    pending_steps_count =  pending_steps_count + 1;
                }
                if (ledger_management.var.steps[load_steps[i]].loading == true) {
                    running_step_count = running_step_count + 1;
                }
	        }
	        if (running_step_count == 0) { 
	            for (let i = 0; i < load_steps.length; i++) {
		            if (ledger_management.var.steps[load_steps[i]].loading == true) {           
			        break;
		        }
                if (ledger_management.var.steps[load_steps[i]].completed == false && ledger_management.var.steps[load_steps[i]].loading == false) {
			       ledger_management.var.steps[load_steps[i]].exec();
			       ledger_management.var.steps[load_steps[i]].loading = true;
			       break;
	            }
	        }
	     }
	     if (pending_steps_count > 1) {                

                setTimeout("ledger_management.init_begin()",50);
	     }
        },
        init_template: function() {
                 if ($("#ledger_ui_account_details").length > 0)  {
                        ledger_management.accounts.init();
                 }

                 if ($("#ledger_ui_identification_details").length > 0) {
                        ledger_management.identification.init();
                 }

                 if ($("#ledger_ui_residential_details").length > 0 || $("#ledger_ui_postal_details").length) {
                        ledger_management.address.init();
                 }

                 if ($("#ledger_ui_contact_details").length > 0) {
                        ledger_management.contact.init();
                 }
                 ledger_management.var.steps['step1'].loading = false;
                 ledger_management.var.steps['step1'].completed = true;
                 ledger_management.var.is_loading = false;
        },
        init_load_order: {
            step1: function() {
                 setTimeout("ledger_management.init_template();",40);
                 

            },
            step2: function() {
               ledger_management.get_settings(); 
            },
            step3: function() {
               ledger_management.get_countries();
            },
            step4: function () {

                 ledger_management.get_account_details();
                 ledger_management.var.csrf_token = $('#ledger_ui_csrf_token').val();
                 ledger_management.accounts.get_data_loading();
                 ledger_management.identification.get_data_loading();
                 ledger_management.address.get_data_loading();
                 ledger_management.contact.get_data_loading();
                 //if ($("#ledger_ui_account_details").length > 0)  {
                 //       ledger_management.accounts.init();                    
                 //}

                 //if ($("#ledger_ui_identification_details").length > 0) {
                 //       ledger_management.identification.init();
                 //}

                 //if ($("#ledger_ui_residential_details").length > 0 || $("#ledger_ui_postal_details").length) {
                 //       ledger_management.address.init();
                 //}
 
                 //if ($("#ledger_ui_contact_details").length > 0) {
                 //       ledger_management.contact.init();           
                 //}
            },
            step5: function() {
                ledger_management.cards.init();            
            }

        },
	update_account_details: function(data) {
		 ledger_management.var.is_loading = true;
                 var data = data;
                 $.ajax({
                     url: '/ledger-ui/api/update-account-details/'+ledger_management.var.data.accounts.user_id+'/',
                     method: "POST",
                     headers: {'X-CSRFToken' : ledger_management.var.csrf_token},
                     data: JSON.stringify({'payload': data,}),
                     contentType: "application/json",
                     success: function(data) {
			            ledger_management.get_account_details();
                        console.log('Success');
                     },
                     error: function (error) {
                          console.log('Error updating account information');
                     },
                 });
        },
        get_account_details: function() {
                       ledger_management.var.is_loading = true;
                       $.ajax({
                           url: '/ledger-ui/api/get-account-details/'+ledger_management.var.data.accounts.user_id+'/',
                           method: 'GET',
                           dataType: 'json',
                           cache: false,
                           contentType: 'application/json',
                           //data: "{}",
                           success: function(response) {
                                for (let i = 0; i < response.config.length; i++) {
                                    key = Object.keys(response.config[i]);
                                    ledger_management.var.config[key[0]] = response.config[i][key[0]];
                                }
                                ledger_management.var.account_data = response.data;
                                ledger_management.var.is_loading = false;
                                ledger_management.var.steps['step4'].loading = false;
                                ledger_management.var.steps['step4'].completed = true;
                                ledger_management.var.information_status = response.information_status;

                           },
                           error: function(error) {
                               $('#div-ledger-ui-accounts').show();
                               $('#div-ledger-ui-accounts-loader').hide();
                               console.log('Error loading account details');
                           },
                       });
        },
        get_settings: function() {
                       ledger_management.var.is_loading = true;
                       $.ajax({
                           url: '/ledger-ui/api/get-settings/',
                           method: 'GET',
                           dataType: 'json',
                           cache: false,
                           contentType: 'application/json',
                           //data: "{}",
                           success: function(response) {
                               for (let i = 0; i < response.config.length; i++) {
                                   key = Object.keys(response.config[i]);
                                   ledger_management.var.config[key[0]] = response.config[i][key[0]];
                               }
                               ledger_management.var.steps['step2'].loading = false;
                               ledger_management.var.steps['step2'].completed = true;
                               ledger_management.var.is_loading = false;
                           },
                           error: function(error) {
                               console.log('Error loading get settings');
                           },
                       });
        },
        get_countries: function() {
                       ledger_management.var.is_loading = true;
                       $.ajax({
                           url: '/ledger-ui/api/get-countries/',
                           method: 'GET',
                           dataType: 'json',
                           contentType: 'application/json',
                           //data: "{}",
                           success: function(response) {
                                ledger_management.var.countries = response.data;
			                    ledger_management.var.steps['step3'].loading = false;
			                    ledger_management.var.steps['step3'].completed = true;
                                ledger_management.var.is_loading = false;
                           },
                           error: function(error) {
                               $('#div-ledger-ui-accounts').show();
                               $('#div-ledger-ui-accounts-loader').hide();
                               console.log('Error loading get countries');
                           },
                       });
        },
	    accounts: { 
		get_data: function() {
                    // $('#div-ledger-ui-accounts').hide();

                    $('#input-ledger-ui-given-name').html(ledger_management.var.account_data.first_name);
                    $('#input-ledger-ui-last-name').html(ledger_management.var.account_data.last_name);
                    if ('dob' in ledger_management.var.account_data) {
                       if (ledger_management.var.account_data.dob != null) { 
  		                    var dob_split = ledger_management.var.account_data.dob.split("/"); 
                            $("#input-ledger-ui-dob").datepicker("update", new Date(dob_split[2], dob_split[1] - 1, dob_split[0]));
		                }
                    } else {
                       $("#input-ledger-ui-dob").val("");
                    }
                    $('#div-ledger-ui-accounts').show();
                    $('#div-ledger-ui-accounts-loader').hide();


                    if (ledger_management.var.config.hasOwnProperty('first_name') == true || ledger_management.var.config.hasOwnProperty('last_name') == true) {
                    } else {
                            $('#div-ledger-ui-account-name').hide();
                    }

                    if (ledger_management.var.config.hasOwnProperty('legal_first_name') == true || ledger_management.var.config.hasOwnProperty('legal_last_name') == true) {
                    } else {
                            $('#div-ledger-ui-legal-name').hide();
                    }

                    if (ledger_management.var.config.hasOwnProperty('dob') == true ) {
                    } else {
                            $('#div-ledger-ui-dob-name').hide();
                    }       
                    
                    

                    if (ledger_management.var.information_status.personal_details_completed == true) { 
                        $('#personal-details-status').html('<i class="bi bi-check-circle-fill" style="color: #08c508;"></i>');

                    } else {
                        $('#personal-details-status').html('<i class="bi bi-x-circle-fill" style="color: #ff0909"></i>');
                    }
                },
                get_data_loading: function() {
                    $('#div-ledger-ui-accounts').hide();
                    $('#div-ledger-ui-accounts-loader').show();

                    if (ledger_management.var.is_loading == false) { 
                       ledger_management.accounts.get_data();
                    } else {
                        setTimeout("ledger_management.accounts.get_data_loading();", 200);
                    }
                },
		update_data: function() {
                    var data = {};
                    var dob = $('#input-ledger-ui-dob');
                    data['dob'] = dob.val();

                    ledger_management.update_account_details(data); 
                    ledger_management.accounts.get_data_loading();
		},
		init: function() {
                    var html = "";
	                html += "<div id='div-ledger-ui-accounts-loader'>"+ledger_management.var.pagesettings.loader+"</div>";
		            html += "<div id='div-ledger-ui-accounts' style='display:none'>";

                    html += "<div id='div-ledger-ui-account-name'>";
                    html += "<div class='ms-3 mb-1 me-3 '><h6>Account Name</h6></div>";
                    html += "  <div class='row mx-md-n5 border p-2 ms-3 me-3 mb-3'>";
                    html += "       <div class='col-3 text-end p-2'>";
                    html += "         ";
                    html += "       </div>";
                    html += "       <div class='col-5 p-2'> ";
                    html += "       <div class='fw-bold'>To update your account name or MFA(Multi-Factor Authentication) please <a href='/sso/setting'>click here</a>:</div>";
                    html += "       <div><small><i>Changes will not update until your next login.</i></small></div>";
                    html += "       </div>";
                    html += "       <div class='col-4  p-2'>";
                    html += "         </span>";
                    html += "       </div>";

                    html += "       <div class='col-3 text-end p-2'>";
                    html += "         <label for='input-ledger-ui-given-name' class='col-form-label fw-bold'>Given name(s)</label>";
                    html += "       </div>";
                    html += "       <div class='col-5 p-2'> ";
                    html += "         <span id='input-ledger-ui-given-name' class='form-control' style='background-color:#efefef' > <span>";
                    html += "       </div>";
                    html += "       <div class='col-4  p-2'>";
                    html += "           <span id='moreinfoInline' class='form-text'>";
                    html += "             ";
                    html += "         </span>";
                    html += "       </div>";

                    html += "       <div class='col-3 text-end p-2'>";
                    html += "         <label for='input-ledger-ui-last-name' class='col-form-label fw-bold'>Surname</label>";
                    html += "       </div>";
                    html += "       <div class='col-5 p-2'>";
                    html += "         <span type='input' id='input-ledger-ui-last-name' class='form-control' style='background-color:#efefef' ><span>";
                    html += "       </div>";
                    html += "       <div class='col-4 p-2'>";
                    html += "         <span id='lineInline' class='form-text'>";
                    html += "         </span>";
                    html += "       </div>";
                    html += "   </div>";
                    html += "</div>";

                    html += "<div id='div-ledger-ui-legal-name'>"; 
                    // Legal Name
                    html += "<div class='ms-3 mb-1 me-3'><h6>Legal Name</h6></div>";
		            html += "  <div class='row mx-md-n5 border p-2 ms-3 me-3 mb-3'>";

                    html += "       <div class='col-3 text-end p-2'>";
                    html += "         <label for='input-ledger-ui-legal-given-name' class='col-form-label fw-bold'>Given name(s)</label>";
                    html += "       </div>";
                    html += "       <div class='col-5 p-2'> ";
                    html += "         <input id='input-ledger-ui-legal-given-name' class='form-control' autocomplete='off'>";
                    html += "       </div>";
                    html += "       <div class='col-4  p-2'>";
                    html += "           <span id='moreinfoInline' class='form-text'>";
                    html += "             ";
                    html += "         </span>";
                    html += "       </div>";

                    html += "       <div class='col-3 text-end p-2'>";
                    html += "         <label for='input-ledger-ui-last-name' class='col-form-label fw-bold'>Surname</label>";
                    html += "       </div>";
                    html += "       <div class='col-5 p-2'>";
                    html += "         <input type='input' id='input-ledger-ui-legal-last-name' class='form-control' autocomplete='off' >";
                    html += "       </div>";
                    html += "       <div class='col-4 p-2'>";
                    html += "         <span id='lineInline' class='form-text'>";
                    html += "         </span>";
                    html += "       </div>";
                    html += "   </div>";
                    html += "   </div>";

	                html += "<div id='div-ledger-ui-dob-name' >";
		            html += "   <div class='row mx-md-n5 border p-2 ms-3 me-3 mb-3'>";
                    html += "       <div class='col-3 text-end p-2'>";
                    html += "         <label for='inputLine2' class='col-form-label fw-bold'>Date of Birth</label>";
                    html += "       </div>";
                    html += "       <div class='col-5 p-2'>";
                    html += "         <input type='input' id='input-ledger-ui-dob' class='form-control bs-datepicker' autocomplete='off'>";
                    html += "       </div>";
                    html += "       <div class='col-4 p-2'>";
                    html += "         <span id='lineInline' class='form-text'>";
                    html += "         </span>";
                    html += "       </div>";
                    html += "   </div>";
                    html += "   <div class='d-grid gap-2 d-md-flex justify-content-md-end'> <button class='pull-right btn btn-primary' id='update-account-details'>Update</button></div>";
                    html += "</div>";
                    html += "</div>";
                    
                    $('#ledger_ui_account_details').html(html);
                    $('.bs-datepicker').datepicker({"format": "dd/mm/yyyy"});

                    $('#update-account-details').click(function() {
			        ledger_management.accounts.update_data();
		     });

		}
	},
        identification: {
                get_data: function() {
                    $('#div-ledger-ui-identification').show();
                    $('#div-ledger-ui-identification-loader').hide();
                },
                get_data_loading: function() {
                    $('#div-ledger-ui-identification').hide();
                    $('#div-ledger-ui-identification-loader').show();

                    if (ledger_management.var.is_loading == false) {
                       ledger_management.identification.get_data();
                    } else {
                         setTimeout("ledger_management.identification.get_data_loading();", 200);
                    }
                },
                update_data: function() {
                    ledger_management.get_account_details();
                    ledger_management.identification.get_data_loading();
                },
                init: function() {
                     // $('#ledger_ui_identification_details').html(ledger_management.var.pagesettings.loader);
                     var html = "";

                     html += "<div id='div-ledger-ui-identification-loader'>"+ledger_management.var.pagesettings.loader+"</div>";
                     html += "<div id='div-ledger-ui-identification' style='display:none'>";

                     html += "<div class='row mx-md-n5'>";
                     html += "       <div class='col-3 text-end p-2'>";
                     html += "         <label for='inputLine1' class='col-form-label fw-bold'>Identification</label>";
                     html += "       </div>";
                     html += "       <div class='col-5 p-2'> ";
                     html += "         <input type='input' id='inputLine1' class='form-control'>";
                     html += "       </div>";
                     html += "       <div class='col-4  p-2'>";
                     html += "           <span id='moreinfoInline' class='form-text'>";
                     html += "             ";
                     html += "         </span>";
                     html += "       </div>";

                     html += " <div class='d-grid gap-2 d-md-flex justify-content-md-end'> <button class='pull-right btn btn-primary' id='update-identification-details'>Update</button></div>";
                     html += "</div>";
                     html += "</div>";


                     $('#ledger_ui_identification_details').html(html);

                     $('#update-identification-details').click(function() {
                             ledger_management.identification.update_data();
                     });
                     // ledger_management.identification.get_data_loading();
                }
        },
	address: {
                get_data: function() {
                     //#input-ledger-ui-residential-address-country
                    var countries_select_html ="";
                    for (let i = 0; i < ledger_management.var.countries.length; i++) {
                        countries_select_html += "<option value='"+ledger_management.var.countries[i].country_code+"'>"+ledger_management.var.countries[i].country_name+"</option>"; 
                    }
                    $('#input-ledger-ui-residential-address-country').html(countries_select_html);
                    $('#input-ledger-ui-postal-address-country').html(countries_select_html);
                    if ('residential_address' in ledger_management.var.config) {
                            //if ('residential_line1' in ledger_management.var.config ) {
                                $('#input-ledger-ui-residential-address-line1').val(ledger_management.var.account_data.residential_address.line1); 
                            //}
                            //if ('residential_locality' in ledger_management.var.config ) {
                                $('#input-ledger-ui-residential-address-locality').val(ledger_management.var.account_data.residential_address.locality);
                            //}
                            //if ('residential_state' in ledger_management.var.config ) {
                                $('#input-ledger-ui-residential-address-state').val(ledger_management.var.account_data.residential_address.state);
                            //}
                            //if ('residential_postcode' in ledger_management.var.config ) {
                                $('#input-ledger-ui-residential-address-postcode').val(ledger_management.var.account_data.residential_address.postcode);
                            //}
                            //if ('residential_country' in ledger_management.var.config ) {
                                $('#input-ledger-ui-residential-address-country').val(ledger_management.var.account_data.residential_address.country);
                            //}
                    }

		    if ('postal_address' in ledger_management.var.config ) {

                    //if ('postal_line1' in ledger_management.var.config ) {
		    // if ('line1' in ledger_management.var.account_data.postal_address) {
                            $('#input-ledger-ui-postal-address-line1').val(ledger_management.var.account_data.postal_address.line1);
		    //     }
                    //}
                    //if ('postal_locality' in ledger_management.var.config ) {
			// if ('locality'  in ledger_management.var.account_data.postal_address) {
                            $('#input-ledger-ui-postal-address-locality').val(ledger_management.var.account_data.postal_address.locality);
		        // }
                    //}
                    //if ('postal_state' in ledger_management.var.config ) {
                         $('#input-ledger-ui-postal-address-state').val(ledger_management.var.account_data.postal_address.state);
                    //}
                    //if ('postal_postcode' in ledger_management.var.config ) {
                         $('#input-ledger-ui-postal-address-postcode').val(ledger_management.var.account_data.postal_address.postcode);
                    //}
                    //if ('postal_country' in ledger_management.var.config ) {
                         $('#input-ledger-ui-postal-address-country').val(ledger_management.var.account_data.postal_address.country);
                    //}
                         if (ledger_management.var.account_data.postal_same_as_residential == true) { 
              			 $('#input-ledger-ui-postal-address-same-as-residential').prop('checked', true);
			 } else {
                                 $('#input-ledger-ui-postal-address-same-as-residential').prop('checked', false);
		         }
                         ledger_management.address.postal_address_disabled();


                   
		    }
		    $('#div-ledger-ui-residential-address').show();
                    $('#div-ledger-ui-residential-address-loader').hide();
                    $('#div-ledger-ui-postal-address').show();
                    $('#div-ledger-ui-postal-address-loader').hide();

                    // if (ledger_management.var.config.hasOwnProperty('residential_line1') == true
                    //    || ledger_management.var.config.hasOwnProperty('residential_locality') == true
		    //	|| ledger_management.var.config.hasOwnProperty('residential_state') == true
		    //	|| ledger_management.var.config.hasOwnProperty('residential_postcode') == true
	            //		|| ledger_management.var.config.hasOwnProperty('residential_country') == true
		    //   ) {
		    if (ledger_management.var.config.hasOwnProperty('residential_address') == true) {
		    } else {
                            $('#div-ledger-ui-residential-address-loader').hide();
			    $('#div-ledger-ui-residential-address').hide();
		    }

                    //if (ledger_management.var.config.hasOwnProperty('postal_line1') == true
                    //    || ledger_management.var.config.hasOwnProperty('postal_locality') == true
                    //    || ledger_management.var.config.hasOwnProperty('postal_state') == true
                    //    || ledger_management.var.config.hasOwnProperty('postal_postcode') == true
                    //    || ledger_management.var.config.hasOwnProperty('postal_country') == true
                    //   ) {
	                if (ledger_management.var.config.hasOwnProperty('postal_address') == true) {
                    } else {
                            $('#div-ledger-ui-postal-address-loader').hide();
                            $('#div-ledger-ui-postal-address').hide();
                    }
                    if (ledger_management.var.config.hasOwnProperty('postal_same_as_residential') == false) {
                        $('#div-ledger-ui-postal-address-same-as-residential').hide();
                    } else {
                        $('#div-ledger-ui-postal-address-same-as-residential').show();
                    }

                    if (ledger_management.var.information_status.address_details_completed == true) { 
                        $('#address-details-status').html('<i class="bi bi-check-circle-fill" style="color: #08c508;"></i>');
                    } else {
                        $('#address-details-status').html('<i class="bi bi-x-circle-fill" style="color: #ff0909"></i>');
                    }      

                },
                get_data_loading: function() {
                    $('#div-ledger-ui-residential-address').hide();
                    $('#div-ledger-ui-residential-address-loader').show();
                    $('#div-ledger-ui-postal-address').hide();
                    $('#div-ledger-ui-postal-address-loader').show();

                    if (ledger_management.var.is_loading == false) {
                       ledger_management.address.get_data();
                    } else {
                       setTimeout("ledger_management.address.get_data_loading();", 500);
                    }
                },
                update_data: function() {
                    var data = {};
                    if ('residential_address' in ledger_management.var.config) {
                                var residential_line1 = $('#input-ledger-ui-residential-address-line1');
                                var residential_locality = $('#input-ledger-ui-residential-address-locality');
                                var residential_state = $('#input-ledger-ui-residential-address-state');
                                var residential_postcode = $('#input-ledger-ui-residential-address-postcode');
                                var residential_country = $('#input-ledger-ui-residential-address-country');
                                data['residential_address'] = {};
                                data['residential_address']['residential_line1'] = residential_line1.val();
                                data['residential_address']['residential_locality'] = residential_locality.val();
                                data['residential_address']['residential_state'] = residential_state.val();
                                data['residential_address']['residential_postcode'] = residential_postcode.val();
                                data['residential_address']['residential_country'] = residential_country.val();
                    }

                    if ('postal_address' in ledger_management.var.config) {                
                        var postal_same_as_residential = $('#input-ledger-ui-postal-address-same-as-residential').is(":checked");
                        var postal_line1 = $('#input-ledger-ui-postal-address-line1');
                        var postal_locality = $('#input-ledger-ui-postal-address-locality');
                        var postal_state = $('#input-ledger-ui-postal-address-state');
                        var postal_postcode = $('#input-ledger-ui-postal-address-postcode');
                        var postal_country = $('#input-ledger-ui-postal-address-country');
                        data['postal_address'] = {}
                        data['postal_address']['postal_line1'] = postal_line1.val();
                        data['postal_address']['postal_locality'] = postal_locality.val();
                        data['postal_address']['postal_state'] = postal_state.val();
                        data['postal_address']['postal_postcode'] =postal_postcode.val();
                        data['postal_address']['postal_country'] = postal_country.val();
                        data['postal_address']['postal_same_as_residential'] = postal_same_as_residential;
                    }

                    

                    ledger_management.update_account_details(data);
                    ledger_management.get_account_details();
                    ledger_management.address.get_data_loading();

                },
                postal_address_disabled: function() {
                             var postaladdresssameasresidential = $('#input-ledger-ui-postal-address-same-as-residential').is(":checked");
                             var postal_line1 = $('#input-ledger-ui-postal-address-line1');
                             var postal_locality = $('#input-ledger-ui-postal-address-locality');
                             var postal_state = $('#input-ledger-ui-postal-address-state');
                             var postal_postcode = $('#input-ledger-ui-postal-address-postcode');
                             var postal_country = $('#input-ledger-ui-postal-address-country');
                             if (postaladdresssameasresidential == true) {
                                      postal_line1.prop('disabled',true);
                                      postal_locality.prop('disabled',true);
                                      postal_state.prop('disabled',true);
                                      postal_postcode.prop('disabled',true);
                                      postal_country.prop('disabled',true);

                             } else {
                                      postal_line1.prop('disabled',false);
                                      postal_locality.prop('disabled',false);
                                      postal_state.prop('disabled',false);
                                      postal_postcode.prop('disabled',false);
                                      postal_country.prop('disabled',false);
                             }
                },
                init: function() {
                    //$('#ledger_ui_residential_details').html(ledger_management.var.pagesettings.loader);

	            // Residential
                    var html = "";
                    html += "<div id='div-ledger-ui-residential-address-loader'>"+ledger_management.var.pagesettings.loader+"</div>";
                    html += "<div id='div-ledger-ui-residential-address' style='display:none'>";

                    html += "<div class='ms-3 mb-1 me-3'><h6>Residential Address</h6></div>";
                    html += "<div class='row mx-md-n5 border p-2 ms-3 me-3 mb-3'>";
                    html += "       <div class='col-3 text-end p-2'>";
                    html += "         <label for='inputLine1' class='col-form-label fw-bold'>Address</label>";
                    html += "       </div>";
                    html += "       <div class='col-5 p-2'> ";
                    html += "         <input type='input' id='input-ledger-ui-residential-address-line1' class='form-control' autocomplete='off'>";
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
                    html += "         <input type='input' id='input-ledger-ui-residential-address-locality' class='form-control' autocomplete='off'>";
                    html += "       </div>";
                    html += "       <div class='col-4 p-2'>";
                    html += "         <span id='lineInline' class='form-text'>";
                    html += "         </span>";
                    html += "       </div>";

                    html += "       <div class='col-3 text-end p-2'>";
                    html += "         <label for='inputLine2' class='col-form-label fw-bold'>State</label>";
                    html += "       </div>";
                    html += "       <div class='col-5 p-2'>";
                    html += "         <input type='input' id='input-ledger-ui-residential-address-state' class='form-control' autocomplete='off'>";
                    html += "       </div>";
                    html += "       <div class='col-4 p-2'>";
                    html += "         <span id='lineInline' class='form-text'>";
                    html += "         </span>";
                    html += "       </div>";

                    html += "       <div class='col-3 text-end p-2'>";
                    html += "         <label for='inputLine2' class='col-form-label fw-bold'>Postcode</label>";
                    html += "       </div>";
                    html += "       <div class='col-5 p-2'>";
                    html += "         <input type='input' id='input-ledger-ui-residential-address-postcode' class='form-control' autocomplete='off'>";
                    html += "       </div>";
                    html += "       <div class='col-4 p-2'>";
                    html += "         <span id='lineInline' class='form-text'>";
                    html += "         </span>";
                    html += "       </div>";

                    html += "       <div class='col-3 text-end p-2'>";
                    html += "         <label for='inputLine2' class='col-form-label fw-bold'>Country</label>";
                    html += "       </div>";
                    html += "       <div class='col-5 p-2'>";
                    html += "        <select class='form-select' id='input-ledger-ui-residential-address-country'></select>";
                    //html += "         <input type='input' id='input-ledger-ui-residential-address-country' class='form-control' autocomplete='off'>";
                    html += "       </div>";
                    html += "       <div class='col-4 p-2'>";
                    html += "         <span id='lineInline' class='form-text'>";
                    html += "         </span>";
                    html += "       </div>";
                    html += " <div class='d-grid gap-2 d-md-flex justify-content-md-end'> <button class='pull-right btn btn-primary' id='update-residential-details'>Update</button></div>";
                    html += "</div>";
                    html += "</div>";

                    $('#ledger_ui_residential_details').html(html);
                    $('#update-residential-details').click(function() {
                            ledger_management.address.update_data();
                    });
                    
                    //$('#ledger_ui_postal_details').html(ledger_management.var.pagesettings.loader);
                    
		            // Postal  ledger_ui_postal_details"
                    var html = "";
                    html += "<div id='div-ledger-ui-postal-address-loader'>"+ledger_management.var.pagesettings.loader+"</div>";
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
                          ledger_management.address.update_data();
                    });
		            $('#input-ledger-ui-postal-address-same-as-residential').click(function(e) {
                             ledger_management.address.postal_address_disabled();
	                });

                }
	},
    contact: {
                get_data: function() {
                    $('#input-ledger-ui-contact-phone').val(ledger_management.var.account_data.phone_number);
                    $('#input-ledger-ui-contact-mobile').val(ledger_management.var.account_data.mobile_number);
                    $('#div-ledger-ui-contact').show();
                    $('#div-ledger-ui-contact-loader').hide();
                    if (ledger_management.var.information_status.contact_details_completed == true) { 
                        $('#contact-details-status').html('<i class="bi bi-check-circle-fill" style="color: #08c508;"></i>');
                    } else {
                        $('#contact-details-status').html('<i class="bi bi-x-circle-fill" style="color: #ff0909"></i>');
                    }   

                },
                get_data_loading: function() {
                    $('#div-ledger-ui-contact').hide();
                    $('#div-ledger-ui-contact-loader').show();

                    if (ledger_management.var.is_loading == false) {
                       ledger_management.contact.get_data();
                    } else {
                       setTimeout("ledger_management.contact.get_data_loading();", 200);
                    }
                },

                update_data: function() {
                    var data = {};
                    var contact_phone = $('#input-ledger-ui-contact-phone');
                    var contact_mobile = $('#input-ledger-ui-contact-mobile');
                    data['phone_number'] = contact_phone.val();
                    data['mobile_number'] = contact_mobile.val();

                    ledger_management.update_account_details(data);
                    ledger_management.get_account_details();
                    ledger_management.contact.get_data_loading();
                },
                init: function() {

                     $('#ledger_ui_contact_details').html(ledger_management.var.pagesettings.loader);

                     var html = "";
                     html += "<div id='div-ledger-ui-contact-loader'>"+ledger_management.var.pagesettings.loader+"</div>";
                     html += "<div id='div-ledger-ui-contact' style='display:none'>";

                     html += "<div class='row mx-md-n5'>";
                     html += "       <div class='col-3 text-end p-2'>";
                     html += "         <label for='inputLine1' class='col-form-label fw-bold'>Phone (work)</label>";
                     html += "       </div>";
                     html += "       <div class='col-5 p-2'> ";
                     html += "         <input type='input' id='input-ledger-ui-contact-phone' class='form-control' autocomplete='off'>";
                     html += "       </div>";
                     html += "       <div class='col-4  p-2'>";
                     html += "           <span id='moreinfoInline' class='form-text'>";
                     html += "             ";
                     html += "         </span>";
                     html += "       </div>";

                     html += "       <div class='col-3 text-end p-2'>";
                     html += "         <label for='inputLine1' class='col-form-label fw-bold'>Mobile</label>";
                     html += "       </div>";
                     html += "       <div class='col-5 p-2'> ";
                     html += "         <input type='input' id='input-ledger-ui-contact-mobile' class='form-control' autocomplete='off'>";
                     html += "       </div>";
                     html += "       <div class='col-4  p-2'>";
                     html += "           <span id='moreinfoInline' class='form-text'>";
                     html += "             ";
                     html += "         </span>";
                     html += "       </div>";

                     html += " <div class='d-grid gap-2 d-md-flex justify-content-md-end'> <button class='pull-right btn btn-primary' id='update-contact-details'>Update</button></div>";
                     html += "</div>";
                     html += "</div>";
                      
                     $('#ledger_ui_contact_details').html(html);

                     $('#update-contact-details').click(function() {
                             ledger_management.contact.update_data();
                     });
                }
        },
        "cards": {
            get_card_data: function() {
                $.ajax({
                    url: '/ledger-toolkit-api/get-card-tokens',
                    method: 'GET',
                    dataType: 'json',
                    contentType: 'application/json',
                    success: function(response) {

                       ledger_management.var.cards = response.card_tokens;
                       ledger_management.var.primary_card_id = response.primary_card
                       ledger_management.cards.display_cards();
                    },
                    error: function(error) {
                            
                    },
                });
            },
            delete_card:function(card_id) {
                $.ajax({
                    url: '/ledger-toolkit-api/delete-card-token/'+card_id+'/',
                    method: 'GET',
                    dataType: 'json',
                    contentType: 'application/json',
                    success: function(response) {
                       ledger_management.cards.get_card_data();
                    },
                    error: function(error) {

                    },
                });
                
	        },
            delete_card_confirm: function(card_id) { 
                $('#DeleteCardConfirmModal').modal('show');
                $('#delete_card_id').val(card_id);
            },
            save_card: function() { 
                var id_number = $('#id_number').val();
                var id_expiry_month_0 = $('#id_expiry_month_0').val();
                var id_expiry_month_1 = $('#id_expiry_month_1').val();
                var ccv = $('#id_ccv').val();

                $('#id_number').prop( "disabled", true );
                $('#id_expiry_month_0').prop( "disabled", true );
                $('#id_expiry_month_1').prop( "disabled", true );
                $('#id_ccv').prop( "disabled", true );               

                $("#save-card-button").hide();
                $("#save_card_loader").show();
                var data = { 
                            'number': id_number, 
                            'expiry_month_0': id_expiry_month_0, 
                            'expiry_month_1': id_expiry_month_1, 
                            'ccv': ccv,
                            'store_card': true
                            };

                $.ajax({
                    url: '/ledger-toolkit-api/store-card/',
                    method: 'POST',
                    dataType: 'json',
                    data: JSON.stringify({'payload': data,}),
                    contentType: 'application/json',
                    success: function(response) {
                       ledger_management.cards.get_card_data();
                       if (response['status'] == 200) {
                            $('#AddNewCardModal').modal('hide');
                            $('#ledger_ui_add_card_message').html('');
                            $('#id_number').val('');
                            $('#id_expiry_month_0').val('');
                            $('#id_expiry_month_1').val('');
                            $('#id_ccv').val('');
                       } else {
                            var error = '';
                            error = response['error'];
                            $('#ledger_ui_add_card_message').html('<div class="alert alert-danger" role="alert">Error adding card, please check your details and try again. '+error+'</div>');                        
                       }

                       $('#id_number').prop( "disabled", false );
                       $('#id_expiry_month_0').prop( "disabled", false );
                       $('#id_expiry_month_1').prop( "disabled", false );
                       $('#id_ccv').prop( "disabled", false );   

                       $("#save-card-button").show();
                       $("#save_card_loader").hide();                       
                    },
                    error: function(error) {
                            alert("Error Saving Store Card");
                    },
                });                             
            },
            primary_display_cards: function() {
                var primary_card = '';
                var html = "";
                html += "<div class='row pt-3 pb-3 ps-5 pe-5'>";
                // html += "<div class='col-1'>Primary Card</div><div class='col-8'>Card</div><div>Action</div>";
                if (ledger_management.var.primary_card_id == null) {
                    primary_card = 'checked';
                }
                html += "<div class='col-8'>&nbsp;&nbsp;&nbsp;&nbsp;<i class='bi bi-credit-card-2-front-fill' style='color: #0037ff;'></i>&nbsp;&nbsp;&nbsp;No card</div><div class='col-4 pt-1'><div class='form-check'><input class='form-check-input' type='radio' name='primary-card' id='flexRadioDefault1' value='-1' "+primary_card+"></div></div>";
                for (let i = 0; i < ledger_management.var.cards.length; i++) {
                    primary_card = '';
                    if (parseInt(ledger_management.var.primary_card_id) == parseInt(ledger_management.var.cards[i].id)) { 
                        primary_card = 'checked';               
                    }
		            html += "<div class='col-8'>&nbsp;&nbsp;&nbsp;&nbsp;<i class='bi bi-credit-card-2-front-fill' style='color: #0037ff;'></i>&nbsp;&nbsp;&nbsp;"+ledger_management.var.cards[i].card_type+" ending "+ledger_management.var.cards[i].last_digits+" with expiry "+ledger_management.var.cards[i].expiry_date+"</div><div class='col-4 pt-1'><div class='form-check'><input class='form-check-input' type='radio' name='primary-card' id='PrimaryCard"+ledger_management.var.cards[i].id+"' value='"+ledger_management.var.cards[i].id+"' "+primary_card+"></div></div>";
                }
                html += "</div>";

                $('#ledger_ui_primary_card_list').html(html);
                

            },
            save_primary_card: function() {
                $("#save-primary-card-button").hide();
                $("#save_primary_card_loader").show();  
                $("input[name=primary-card]").prop( "disabled", true );

                var default_card_id = $("input[name=primary-card]:checked").val();
                var data = {"default_card_id": default_card_id};

                $.ajax({
                    url: '/ledger-toolkit-api/set-primary-card/',
                    method: 'POST',
                    dataType: 'json',
                    data: JSON.stringify({'payload': data,}),
                    contentType: 'application/json',
                    success: function(response) {
                       ledger_management.cards.get_card_data();
                       if (response['status'] == 200) {
                            $('#PrimaryCardModal').modal('hide');
                       } else {
                            var error = '';
                            error = response['error'];
                            $("input[name=primary-card]").prop( "disabled", false );
                            $('#ledger_ui_add_card_message').html('<div class="alert alert-danger" role="alert">Error adding card, please check your details and try again. '+error+'</div>');                        
                       }

                       $("#save-primary-card-button").show();
                       $("#save_primary_card_loader").hide();     
                                             
                    },
                    error: function(error) {
                        alert("Error Saving Primary Card");
                    },
                });    


            },
            display_cards: function() {
                var html = "";
                html += "<div class='row pt-3 pb-3 ps-5 pe-5'>";
                // html += "<div class='col-1'>Primary Card</div><div class='col-8'>Card</div><div>Action</div>";
                var primary_card_html = "";
                
                for (let i = 0; i < ledger_management.var.cards.length; i++) {
                     primary_card_html = "";
                     if (parseInt(ledger_management.var.primary_card_id) == parseInt(ledger_management.var.cards[i].id)) { 
                        // primary_card_html = "<button class='btn btn-sm btn-danger'>PRIMARY CARD</button>";
                        primary_card_html = '<i class="bi bi-check-circle-fill" style="font-size: 24px; color: #1cb352;">&nbsp;</i>';
                     }
                     
		             html += "<div class='col-8'>&nbsp;&nbsp;&nbsp;&nbsp;<i class='bi bi-credit-card-2-front-fill' style='color: #0037ff;'></i>&nbsp;&nbsp;&nbsp;"+ledger_management.var.cards[i].card_type+" ending "+ledger_management.var.cards[i].last_digits+" with expiry "+ledger_management.var.cards[i].expiry_date+"</div><div class='col-1'>"+primary_card_html+"</div><div class='col-3 pt-1 text-end'><button class='btn btn-sm btn-primary m-1' onclick='ledger_management.cards.delete_card_confirm("+'"'+ledger_management.var.cards[i].id+'"'+");'>Remove Card</button></div>";
                }
                html += "</div>";

                $('#div-ledger-ui-list-card-details').html(html);
                $('#div-ledger-ui-card-details').show();
                $('#div-ledger-ui-card-details-loader').hide();
            },
            init: function() {
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
                        $('#nav-cards-tab-page').hide();

                        $('.managed-account-nav').click(function() {
                            $('.managed-account-nav').each(function(i, obj) {                               
                                $("#"+obj.id+'-page').hide();
                            });
                            $("#"+this.id+'-page').show();                          
                        });
                        ledger_management.var.steps['step5'].loading = false;
                        ledger_management.var.steps['step5'].completed = true;
    

                } else {
                    ledger_management.var.steps['step5'].loading = false;
                    ledger_management.var.steps['step5'].completed = true;
                }
            }

        }
	
}
