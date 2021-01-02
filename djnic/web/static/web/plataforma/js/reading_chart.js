    google.charts.load('current', {'packages':['corechart', 'bar']});
    google.charts.setOnLoadCallback(drawChart);

    
    function drawChart() {

        var chartDiv = document.getElementById('chart_div');

        var jsonData = $.ajax({
            url: "/api/v1/dominios/stats/reading?p=2",
            dataType: "json",
            async: false
            });

        var data = google.visualization.arrayToDataTable(jsonData.responseJSON.data.google_chart_data);

        var materialOptions = {
            isStacked: true,
            chart: {
                title: 'Lectura de dominios',
                subtitle: 'Dias desde ultima lectura por dia de vencimiento de dominio'
                },
            }

        var materialChart = new google.charts.Bar(chartDiv);
        materialChart.draw(data, google.charts.Bar.convertOptions(materialOptions));
    }