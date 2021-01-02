google.charts.load('current', {'packages':['corechart', 'bar']});
google.charts.setOnLoadCallback(drawCharts);


function drawCharts() {
    drawChart1();
    drawChart2();
}

function drawChart1() {

    var chartDiv1 = document.getElementById('chart_div1');

    var jsonData = $.ajax({
        url: "/api/v1/dominios/stats/reading",
        dataType: "json",
        async: false
        });

    var data = google.visualization.arrayToDataTable(jsonData.responseJSON.data.google_chart_data);

    var materialOptions = {
        isStacked: true,
        chart: {
            title: 'Lectura de dominios',
            subtitle: 'Dias desde ultima lectura por dia de vencimiento de dominio',
            legend: { position: "none" },
            },
        }

    var materialChart = new google.charts.Bar(chartDiv1);
    materialChart.draw(data, google.charts.Bar.convertOptions(materialOptions));
}

function drawChart2() {

    var chartDiv2 = document.getElementById('chart_div2');

    var jsonData = $.ajax({
        url: "/api/v1/dominios/stats/reading/-300/420",
        dataType: "json",
        async: false
        });

    var data = google.visualization.arrayToDataTable(jsonData.responseJSON.data.google_chart_data);

    var materialOptions = {
        isStacked: true,
        chart: {
            title: 'Lectura de dominios',
            subtitle: 'Dias desde ultima lectura por dia de vencimiento de dominio',
            legend: { position: "none" },
            },
        }

    var materialChart = new google.charts.Bar(chartDiv2);
    materialChart.draw(data, google.charts.Bar.convertOptions(materialOptions));
}