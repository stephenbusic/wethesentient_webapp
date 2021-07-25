// SUBS CHART
    // Create Subs graph as soon as page is ready
    $(document).ready(function() {

        // create an AJAX call
        $.ajax({
            type: "get",
            url: subs_data_url,
            data: {
                'csrfmiddlewaretoken': csrf_token
            },

            // If call returns successful, continue to build graph
            success: function(data) {

                // Get sub data
                var SubData = data;

                // Get and display total subs
                document.getElementById("total_subs").innerHTML = "TOTAL SUBS: " + SubData['total_subs'];

                // Get element in document to replace with graph
                const ctx = document.getElementById('SubsChart').getContext('2d');

                // Parse the dates to JS
                SubData['chart_data'].forEach((d) => {
                    d.x = new Date(d.date);
                });

                // Render the chart
                const chart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        datasets: [
                            {
                                label: 'Subscribers',
                                data: SubData['chart_data'],
                                backgroundColor: 'rgba(66, 245, 72, 0.5)',
                            },
                        ],
                    },
                    options: {
                        responsive: true,
                        scales: {
                            xAxes: [
                                {
                                    type: 'time',
                                    time: {
                                        unit: 'day',
                                        round: 'day',
                                        displayFormats: {
                                            day: 'MMM D',
                                        },
                                    },
                                },
                            ],
                            yAxes: [
                                {
                                    ticks: {
                                        beginAtZero: true,
                                    },
                                },
                            ],
                        },
                    },
                });
            },

            // If ajax call failed, dont display graph
            error: function(data) {
                console.log("Ajax error occurred while trying to retrieve sub data.")
            }
        });
    });

// VIEWS CHART

    // Create Subs graph as soon as page is ready
    $(document).ready(function() {

        // create an AJAX call
        $.ajax({
            type: "get",
            url: views_data_url,
            data: {
                'csrfmiddlewaretoken': csrf_token
            },

            // If call returns successful, continue to build graph
            success: function(data) {

                // Get sub data
                var ViewData = data;

                // Get and display total subs
                document.getElementById("total_views").innerHTML = "TOTAL VIEWS: " + ViewData['total_views'];

                // Get element in document to replace with graph
                const ctx = document.getElementById('ViewsChart').getContext('2d');

                // Parse the dates to JS
                ViewData['chart_data'].forEach((d) => {
                    d.x = new Date(d.date);
                });

                // Render the chart
                const chart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        datasets: [
                            {
                                label: 'Views',
                                data: ViewData['chart_data'],
                                backgroundColor: 'rgba(66, 245, 72, 0.5)',
                            },
                        ],
                    },
                    options: {
                        responsive: true,
                        tension: 0.1,
                        scales: {
                            xAxes: [
                                {
                                    type: 'time',
                                    time: {
                                        unit: 'day',
                                        round: 'day',
                                        displayFormats: {
                                            day: 'MMM D',
                                        },
                                    },
                                },
                            ],
                            yAxes: [
                                {
                                    ticks: {
                                        beginAtZero: true,
                                    },
                                },
                            ],
                        },
                    },
                });
            },

            // If ajax call failed, dont display graph
            error: function(data) {
                console.log("Ajax error occurred while trying to retrieve sub data.")
            }
        });
    });