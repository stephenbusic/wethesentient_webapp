	$(document).ready(function() {

		// Add event listeners once document is ready
		addEvents();
	});

	function addEvents() {

		const reply_buttons = document.querySelectorAll('.reply_click');
		reply_buttons.forEach(function(currentBtn){

			// Get clicked id for each reply_click button in page
			var clicked_id = currentBtn.id.split('reply_click_')[1];

			// Add show and hide events to their cooresponding buttons
			$("#reply_click_" + clicked_id).click(function() { show_reply_form(clicked_id) });
			$("#hide_reply_click_" + clicked_id).click(function() { hide_reply_form(clicked_id) });
		});
	}

	// Function for showing reply forms
	function show_reply_form(clicked_id) {

		// Get and show current reply form
		var current_form = $("#reply_form_" + clicked_id);
		current_form.show();

		// Hide all other reply forms
		const reply_buttons = document.querySelectorAll('.reply_form');
		reply_buttons.forEach(function(currentBtn){

			// Get clicked id for each reply form button in page
			var checked_id = currentBtn.id.split('reply_form_')[1];

			if (checked_id !== clicked_id) {
				var other_form = $("#reply_form_" + checked_id);
				other_form.hide();
			}
		});
	}

	// Function for hiding reply forms
	function hide_reply_form(clicked_id) {

		// Hide current reply form
		var current_form = $("#reply_form_" + clicked_id);
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


		// Add reCaptcha Verficiation to each of the reply forms
		const reply_forms = document.querySelectorAll('.reply_form');
		reply_forms.forEach(function(currentBtn){

			// Get clicked id for each reply_form in page
			var clicked_id = currentBtn.id.split('reply_form_')[1];
			$("#reply_form_" + clicked_id).submit(function(e){
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