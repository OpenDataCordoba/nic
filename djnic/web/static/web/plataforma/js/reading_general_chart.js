google.charts.load('current', {'packages':['corechart', 'bar']});
google.charts.setOnLoadCallback(drawCharts);


function drawCharts() {
    drawChart1();
}

function drawChart1() {

    var chartDiv1 = document.getElementById('chart_div1');
    var chartDiv2 = document.getElementById('chart_div2');
    var chartDiv3 = document.getElementById('chart_div3');

    var jsonData = $.ajax({
        url: "/api/v1/dominios/stats/general?p=3",
        dataType: "json",
        async: false
        });

    var data = google.visualization.arrayToDataTable(jsonData.responseJSON.data.google_chart_data.hora);

    var materialOptions = {
        chart: {
            title: 'Lectura de dominios por hora'},
            legend: { position: "none" },
        }
    var materialChart = new google.charts.Bar(chartDiv1);
    materialChart.draw(data, google.charts.Bar.convertOptions(materialOptions));

    var data = google.visualization.arrayToDataTable(jsonData.responseJSON.data.google_chart_data.dia);
    var materialOptions = {
        chart: {
            title: 'Lectura de dominios por día'},
            legend: { position: "none" },
        }
    var materialChart = new google.charts.Bar(chartDiv2);
    materialChart.draw(data, google.charts.Bar.convertOptions(materialOptions));

    var data = google.visualization.arrayToDataTable(jsonData.responseJSON.data.google_chart_data.semana);
    var materialOptions = {
        chart: {
            title: 'Lectura de dominios por semana'},
            legend: { position: "none" }
        }
    var materialChart = new google.charts.Bar(chartDiv3);
    materialChart.draw(data, google.charts.Bar.convertOptions(materialOptions));
}