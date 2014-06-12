google.load("visualization", "1", {packages:["corechart"]});
google.setOnLoadCallback(drawChart);

try {
    var autobahn = require('autobahn');
} catch (e) {
    // when running in browser, AutobahnJS will
    // be included without a module system
}


function drawChart() {
    var options = {
        title: 'Realtime position',
        hAxis: {
            viewWindow: { min: 0, max: 600 }
        },
        vAxis: {
            viewWindow: { min: 0, max: 500 }
        },
        legend: 'none',
        colors: ['#087037'],
        animation: {
            duration: 200,
        }
    };

    var chart = new google.visualization.ScatterChart(document.getElementById('chart_div'));

    var connection = new autobahn.Connection({
        url: 'ws://127.0.0.1:8080/ws',
        realm: 'realm1'}
                                            );
    var data;

    connection.onopen = function (session) {

        function onevent1(args) {
            data = google.visualization.arrayToDataTable(args[0]);

            console.log("Got event:", args[0]);
            chart.draw(data, options);
        }

        session.subscribe('com.myapp.topic1', onevent1);
    };

    connection.open();

};


