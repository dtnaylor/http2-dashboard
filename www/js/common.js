function plot_cdf(container, title, data, series_keys, series_labels, data_key, verb, value_suffix) {
	// Build highcharts series entries
	series = [];
	for (var i = 0; i < series_keys.length; i++) {
		var key = series_keys[i];
		series.push({
			type: 'line',
			name: series_labels[key],
			data: data['protocol_data'][key][data_key + '_cdf']
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
			xAxis: {
			},
			yAxis: {
				min: 0,
				max: 1,
				title: {
					text: 'CDF'
				}
			},
			tooltip: {
				shared: true,
				headerFormat: '',
				pointFormatter: function() {
					return '<span style="color:' + this.color + '">\u25CF</span> ' +
						this.series.name + ': <b>' + (this.y * 100).toFixed(2) + 
						'%</b> of sites ' + verb + ' <b>' + Math.round(this.x) + 
						'</b> or fewer ' + value_suffix + '<br>';
				},
			},
			legend: {
				enabled: true,
			},
			plotOptions: {
				line: {
					marker: {
						enabled: false,
					}
				}
			},

			series: series,
		});
	});

}
