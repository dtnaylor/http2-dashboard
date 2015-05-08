---
---

$.getJSON('{{ site.baseurl }}/data/task_completion.json', function(data) {
	fill_date_menu("tasks-date-menu", data, "set_tasks_crawl_date");
	set_tasks_crawl_date(0);  // start with most recent crawl date
});


function set_tasks_crawl_date(index) {
	$.getJSON('{{ site.baseurl }}/data/task_completion.json', function(data) {
		
		// set display date
		display = document.getElementById("tasks-date-display");
		display.innerHTML = data[index].pretty_date;


		$(function () {
			$('#completion-time').highcharts({

				chart: {
					type: 'column',
					zoomType: 'x',
				},
				title: {
					text: 'Task Completion Times',
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
					data: data[index]['times'],
				}]
			});
		});
	});
}
