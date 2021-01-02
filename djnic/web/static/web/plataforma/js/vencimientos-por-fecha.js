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
        url: "/api/v1/dominios/stats/vencimientos-por-fecha",
        dataType: "json",
        async: false
        });

    var data = google.visualization.arrayToDataTable(jsonData.responseJSON.data.google_chart_data.year);

    var materialOptions = {
        chart: {
            title: 'Dominios que vencen por año'},
            legend: { position: "none" },
        }
    var materialChart = new google.charts.Bar(chartDiv1);
    materialChart.draw(data, google.charts.Bar.convertOptions(materialOptions));

    var data = google.visualization.arrayToDataTable(jsonData.responseJSON.data.google_chart_data.day);
    var materialOptions = {
        chart: {
            title: 'Dominios que vencen cada día'},
            legend: { position: "none" },
        }
    var materialChart = new google.charts.Bar(chartDiv2);
    materialChart.draw(data, google.charts.Bar.convertOptions(materialOptions));

    var data = google.visualization.arrayToDataTable(jsonData.responseJSON.data.google_chart_data.week);
    var materialOptions = {
        chart: {title: 'Dominios que vencen cada semana'},
        legend: { position: "none" },
    }
    var materialChart = new google.charts.Bar(chartDiv3);
    materialChart.draw(data, google.charts.Bar.convertOptions(materialOptions));
}