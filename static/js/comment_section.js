	$(document).ready(function() {

		// Add event listeners once document is ready
		addEvents();
	});

	function addEvents() {

		const dropdown_buttons = document.querySelectorAll('.dropdown_click');
		dropdown_buttons.forEach(function(currentBtn){

			// Get clicked id for each dropdown_click button in page
			var clicked_id = currentBtn.id.split('dropdown_click_')[1];

			// Add show and hide events to their cooresponding buttons
			$("#dropdown_click_" + clicked_id).click(function() { show_dropdown_form(clicked_id) });
			$("#hide_dropdown_click_" + clicked_id).click(function() { hide_dropdown_form(clicked_id) });
		});
	}

	// Function for showing dropdown forms
	function show_dropdown_form(clicked_id) {

		// Get and show current dropdown form
		var current_form = $("#dropdown_form_" + clicked_id);
		current_form.show();

		// Hide all other dropdown forms
		const dropdown_buttons = document.querySelectorAll('.dropdown_form');
		dropdown_buttons.forEach(function(currentBtn){

			// Get clicked id for each dropdown form button in page
			var checked_id = currentBtn.id.split('dropdown_form_')[1];

			if (checked_id !== clicked_id) {
				var other_form = $("#dropdown_form_" + checked_id);
				other_form.hide();
			}
		});
	}

	// Function for hiding dropdown forms
	function hide_dropdown_form(clicked_id) {

		// Hide current dropdown form
		var current_form = $("#dropdown_form_" + clicked_id);
		current_form.hide();
	}

	// When reCaptcha v3 is ready, add verifications to each form submit button
	grecaptcha.ready(function() {

		// Add reCaptcha Verficiation to the static comment form
		$("#comment_form").submit(function(e) {
			var form = this;

			e.preventDefault();
			grecaptcha.execute(site_key, {action: 'submit'}).then(function(token) {

				// Add token to hidden recaptcha input field
				document.getElementById("recaptcha").value = token;
				form.disabled = true;
				form.submit();
				form.reset();
			});
		});

		// Add reCaptcha Verficiation to each of the dropdown forms
		const dropdown_forms = document.querySelectorAll('.dropdown_form');
		dropdown_forms.forEach(function(currentBtn){

			// Get clicked id for each dropdown_form in page
			var clicked_id = currentBtn.id.split('dropdown_form_')[1];

            // If delete button exists and was clicked, set value
            // of the hidden input field "edit_type" to "delete"
            if ( $('#delete_' + clicked_id).length ) {
                $('#delete_' + clicked_id).click(function() {
                    document.getElementById("is_deletion_" + clicked_id).value = "true";
                });
            }

            // Add reCaptcha Verficiation to the static dropdown form
			$("#dropdown_form_" + clicked_id).submit(function(e){
				var form = this;

				e.preventDefault();
				grecaptcha.execute(site_key, {action: 'submit'}).then(function(token) {

					// Add token to hidden recaptcha input field
					document.getElementById("recaptcha_" + clicked_id).value = token;
					form.disabled = true;
					form.submit();
					form.reset();
				});
			});
		});
	});