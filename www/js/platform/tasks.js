---
---
$.getJSON('{{ site.baseurl }}/data/task_completion.json', function(data) {
	// for now, just show most recent crawl
	var crawl_data = data[0];

	$(function () {
		$('#completion-time').highcharts({

			chart: {
				type: 'column',
				zoomType: 'x',
			},
			title: {
				text: 'Task Completion Times (' + crawl_data['pretty_date'] + ')',
			},

			xAxis: {
				title: {
					text: 'Seconds'
				}
			},

			yAxis: {
				title: {
					text: 'Number of Tasks'
				}
			},

			tooltip: {
				formatter: function() {
					return '<b>' + this.y + '</b> tasks took <b>' + this.x + '</b> seconds to complete.';
				},
			},
			legend: {
				enabled: false,
			},
			plotOptions: {
				column: {
					pointPadding: 0,
					borderWidth: 0,
					groupPadding: 0,
					shadow: false
				}
			},
			series: [{
				data: crawl_data['times'],
			}]
		});
	});
});
