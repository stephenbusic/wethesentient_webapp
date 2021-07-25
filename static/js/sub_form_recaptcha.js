		// When reCaptcha v3 is ready, add verifications to each form submit button
		grecaptcha.ready(function() {

			// Add reCaptcha Verficiation to the static comment form
			$("#subscription_form").submit(function(e) {
                var form = this;

                e.preventDefault();
                grecaptcha.execute(site_key, {action: 'submit'}).then(function(token) {

					// Add token to hidden recaptcha input field
					document.getElementById("recaptcha_sub").value = token;
					form.disabled = true;
                    form.submit();
   					form.reset();
            	});
            });
		});