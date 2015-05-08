---
---
	
$.getJSON('{{ site.baseurl }}/data/active_workers.json', function(data) {
	fill_date_menu("workers-date-menu", data, "set_workers_crawl_date");
	set_workers_crawl_date(0);  // start with most recent crawl date
});

function set_workers_crawl_date(index) {
	$.getJSON('{{ site.baseurl }}/data/active_workers.json', function(data) {
		
		// set display date
		display = document.getElementById("workers-date-display");
		display.innerHTML = data[index].pretty_date;


		$(function () {
			$('#active-workers').highcharts({
				chart: {
					zoomType: 'x'
				},
				title: {
					text: 'Active Workers',
				},
				subtitle: {
					text: document.ontouchstart === undefined ?
							'Click and drag in the plot area to zoom in' :
							'Pinch the chart to zoom in'
				},
				xAxis: {
					type: 'datetime',
					title: {
						text: 'Time (hours)',
					},
					minRange: 10 * 60 * 1000, // 10 minutes
					dateTimeLabelFormats: { 
						day: '%H:%M',
					},
				},
				yAxis: {
					min: 0,
					title: {
						text: 'Number of Workers'
					}
				},
				tooltip: {
					shared: true,
					headerFormat: '<span style="font-size: 10px">Time elapsed: {point.key}</span><br/>',
					xDateFormat: '%H:%M:%S',
				},
				legend: {
					enabled: false,
				},

				series: [{
					type: 'line',
					name: 'Active Workers',
					data: data[index]['counts']
				}],
			});
		});
	});
}
