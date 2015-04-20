$.getJSON('/data/support_by_date.json', function(data) {
	plot_time_series('#advertised-vs-actual-chart',
		'Announced Support vs. Actual Support',
		data,
		['advertised_support_by_date', 'actual_support_by_date'],
		['Announced Support', 'Actual Support']);
	
	plot_time_series('#draft-versions-chart',
		'Version Comparison',
		data,
		[
		'spdy_2',
		'spdy_3',
		'spdy_3.1',
		'h2_12_advertised_support_by_date',
		'h2_14_advertised_support_by_date',
		'h2_15_advertised_support_by_date',
		'h2_16_advertised_support_by_date',
		'h2_17_advertised_support_by_date'],
		['SPDY 2', 'SPDY 3', 'SPDY 3.1',
		 'H2 Draft 12', 'H2 Draft 14', 'H2 Draft 15', 'H2 Draft 16', 'H2 Draft 17']
		);

});

$.getJSON('/data/support_by_country.json', function(data) {
	plot_map('#actual-support-map',
		'Actual Support by Country',
		data);
});



function plot_time_series(container, title, data, series_keys, series_labels) {
	// Build highcharts series entries
	series = [];
	for (var i = 0; i < series_keys.length; i++) {
		var key = series_keys[i];
		series.push({
			type: 'line',
			name: series_labels[i],
			pointInterval: data[key]['interval'],
			pointStart: Date.UTC(data[key]['start_year'],
								 data[key]['start_month'], 
								 data[key]['start_day']),
			data: data[key]['counts']
		});
	}

	$(function () {
		$(container).highcharts({
			chart: {
				zoomType: 'x'
			},
			title: {
				text: title,
			},
			subtitle: {
				text: document.ontouchstart === undefined ?
						'Click and drag in the plot area to zoom in' :
						'Pinch the chart to zoom in'
			},
			xAxis: {
				type: 'datetime',
				minRange: 14 * 24 * 3600000 // fourteen days
			},
			yAxis: {
				min: 0,
				//type: 'logarithmic',
				title: {
					text: 'Number of Domains'
				}
			},
			tooltip: {
				shared: true,
				valueSuffix: ' domains',
			},
			legend: {
				enabled: true,
			},
			plotOptions: {

			},

			series: series,
		});
	});

}

function plot_map(container, title, data) {
	$(function () {
		// Initiate the chart
		$(container).highcharts('Map', {

			title : {
				text : title
			},

			mapNavigation: {
				enabled: true,
				buttonOptions: {
					verticalAlign: 'bottom'
				}
			},

			colorAxis: {
				min: 1,
				max: 1000,
				type: 'logarithmic'
			},

			series : [{
				data : data['values'],
				mapData: Highcharts.maps['custom/world'],
				joinBy: ['iso-a2', 'code'],
				name: 'Population density',
				borderColor: 'black',
				borderWidth: 0.2,
				states: {
					hover: {
						borderWidth: 1
					}
				},
				tooltip: {
					valueSuffix: ' domains'
				}
			}]
		});
	});

}
