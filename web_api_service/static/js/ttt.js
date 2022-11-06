    <script>
        console.log({{ json_datasets|safe }})
        console.log({{ json_labels|safe }})
        /*
        let areaChartData = {
            labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
            datasets: [
                {
                    label: 'Digital Goods',
                    backgroundColor: 'rgba(60,141,188,0.9)',
                    borderColor: 'rgba(60,141,188,0.8)',
                    pointRadius: false,
                    pointColor: '#3b8bba',
                    pointStrokeColor: 'rgba(60,141,188,1)',
                    pointHighlightFill: '#fff',
                    pointHighlightStroke: 'rgba(60,141,188,1)',
                    data: [0, 0, 0, 19, 86, 27, 90]
                },
                {
                    label: 'Electronics',
                    backgroundColor: 'rgba(210, 214, 222, 1)',
                    borderColor: 'rgba(210, 214, 222, 1)',
                    pointRadius: false,
                    pointColor: 'rgba(210, 214, 222, 1)',
                    pointStrokeColor: '#c1c7d1',
                    pointHighlightFill: '#fff',
                    pointHighlightStroke: 'rgba(220,220,220,1)',
                    data: [65, 59, 80, 81, 56, 55, 40]
                },
            ]
        }
        */

        let barChartDataDB = {
            labels: {{ json_labels|safe }},
            datasets: {{ json_datasets|safe }}
        }

        //---------------------
        //- STACKED BAR CHART -
        //---------------------
        let stackedBarChartCanvas = $('#stackedBarChart').get(0).getContext('2d')
        {#let stackedBarChartData = jQuery.extend(true, {}, barChartData)#}

        let stackedBarChartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                xAxes: [{
                    stacked: true,
                }],
                yAxes: [{
                    stacked: true
                }]
            }
        }

        let stackedBarChart = new Chart(stackedBarChartCanvas, {
            type: 'bar',
            data: barChartDataDB,
            options: stackedBarChartOptions
        })


            $.ajax({
            method: "GET",
            url: endpoint,
            success: function (data) {
                console.log(data)
                labels = data.labels
                datasets = data.datasets

            },
            error: function (error_data) {
                console.log('Error')
                console.log(error_data)
            }
        })