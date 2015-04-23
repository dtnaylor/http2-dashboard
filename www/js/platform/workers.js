$.getJSON('/data/active_workers.json', function(data) {

	// for now, just show most recent crawl
	var crawl_data = data[0];

	$(function () {
		$('#active-workers').highcharts({
			chart: {
				zoomType: 'x'
			},
			title: {
				text: 'Active Workers (' + crawl_data['pretty_date'] + ')',
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
				data: crawl_data['counts']
			}],
		});
	});
});
