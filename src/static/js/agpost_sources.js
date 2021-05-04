    $(document).ready(function() {

		//Add toggle "show sources" function to button
		$("#sources_click").click(function() {	show_sources() });
		$("#sources").hide();
	});

	// Function for showing sources
	function show_sources() {

		// Get sources div
		var sources_div = $("#sources");
		var sources_btn = $("#sources_click");

		// If sources is hidden, show. Else, hide.
		if (sources_div.is(":hidden")) {
			sources_div.show();
			sources_btn.val("Hide Sources");
		} else {
			sources_div.hide();
			sources_btn.val("Show Sources");
		}
		sources_btn.blur();
	}