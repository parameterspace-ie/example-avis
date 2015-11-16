// This must be included for javascript to safely post to Django
function csrfSafeMethod(method){
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings){
        var csrftoken = $.cookie('csrftoken');
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

var chartold; // create global

function view_result(url){
    init_chart(function(){
        load_result(url);
    });
}

function init_chart(data_loader){
    chartold = new Highcharts.Chart({
        chart: {
            type: 'scatter',
            zoomType: 'xy',
            
            renderTo: 'container',
            events: {
                load: data_loader
            }
        },
        title: {
            text: 'Sample GACS request'
        },
        subtitle: {
            text: 'Solar mass versus Orbit period'
        },
        xAxis: {
            title: {
                enabled: true,
                text: 'Solar Mass'
            },
            startOnTick: true,
            endOnTick: true,
            showLastLabel: true
        },
        yAxis: {
            startOnTick: true,
            type: 'logarithmic',
            title: {
                text: 'Orbital Period'
            }
        },
        exporting: {
            enabled: true
        },
        legend: {
            layout: 'vertical',
            align: 'left',
            verticalAlign: 'top',
            x: 100,
            y: 70,
            floating: true,
            backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
            borderWidth: 1
        },
        plotOptions: {
            scatter: {
                marker: {
                    radius: 3,
                    states: {
                        hover: {
                            enabled: true,
                            lineColor: 'rgb(100,100,100)'
                        }
                    }
                },
                states: {
                    hover: {
                        marker: {
                            enabled: false
                        }
                    }
                },
                tooltip: {
                    pointFormat: '{point.x} M, {point.y} Days'
                }
            }
        },series: [{
            name: 'GACS Query Data',
            color: 'rgba(223, 83, 83, .5)'
        }]
    });  
}

function load_result(url) {
    console.log("Loading data from " + url);
    $.ajax({
        url: url,
        success: function(resultdata) {
            console.log(resultdata['data']);
            chartold.series[0].setData(resultdata['data']);
        },
        cache: false
    });
}
