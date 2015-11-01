---
---
$.getJSON('{{ site.baseurl }}/data/lists.json', function(data) {
	var announce_link = document.getElementById('h2-announce-list-link');
	announce_link.href = '{{ site.baseurl }}/' + data['h2-announce-list'];
	
	var announce_link = document.getElementById('h2-partial-list-link');
	announce_link.href = '{{ site.baseurl }}/' + data['h2-partial-list'];
	
	var announce_link = document.getElementById('h2-true-list-link');
	announce_link.href = '{{ site.baseurl }}/' + data['h2-true-list'];
});

$.getJSON('{{ site.baseurl }}/data/support_by_date.json', function(data) {
	plot_time_series('#advertised-vs-actual-chart',
		'Announced, Partial, and True Support',
		data,
		['advertised_support_by_date', 'partial_support_by_date', 'true_support_by_date'],
		['Announced Support', 'Partial Support', 'True Support'],
		['#F0AD4E', '#5BC0DE', '#5CB85C'],
		false);
	
	plot_time_series('#draft-versions-chart',
		'Breakdown by Protocol Version (Announced Support)',
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
		 'H2 Draft 12', 'H2 Draft 14', 'H2 Draft 15', 'H2 Draft 16', 'H2 Draft 17'],
		 null,
		 false
		);
	
	plot_time_series('#aux-protocols-chart',
		'Auxiliary Protocols',
		data,
		[
		'npn',
		'alpn',
		'alpn-no-npn',
		'h2c-announce',
		'h2c-support',
		],
		[
		'NPN',
		'ALPN',
		'ALPN without NPN',
		'H2C (Announced)',
		'H2C (True)',
		],
		 null,
		 true
		);

});

$.getJSON('{{ site.baseurl }}/data/support_by_server.json', function(data) {
	plot_time_series('#server-chart',
		'Breakdown by Server (True Support)',
		data['time_series'],
		data['keys'],
		data['keys'],
		null,
		true
		);
});

$.getJSON('{{ site.baseurl }}/data/support_by_country.json', function(data) {
	fill_date_menu("country-date-menu", data, "set_country_crawl_date");
	set_country_crawl_date(0);  // start with most recent data
});

$.getJSON('{{ site.baseurl }}/data/support_by_organization.json', function(data) {
	fill_date_menu("org-date-menu", data, "set_org_crawl_date");
	set_org_crawl_date(0);  // start with most recent data
});




// TODO: Save data in session storage?
function set_country_crawl_date(index) {
	$.getJSON('{{ site.baseurl }}/data/support_by_country.json', function(data) {

		// set display date
		display = document.getElementById("country-date-display");
		display.innerHTML = data[index].pretty_date;

		// load data into map
		plot_map('#actual-support-map',
			'Actual Support by Country',
			data[index]);
	});
}


// TODO: Save data in session storage?
function set_org_crawl_date(index) {
	$.getJSON('{{ site.baseurl }}/data/support_by_organization.json', function(data) {

		// set display date
		display = document.getElementById("org-date-display");
		display.innerHTML = data[index].pretty_date;

		// load data into table
		$('#org-table').DataTable( {
			data: data[index]['values'],
			order: [[ 1, 'desc' ]],  // initially sort by count
			destroy: 'true', // make it possible to load new data
			columns: [
				{ data: 'name' },
				{ data: 'value' }
			]
		} );
	});
}




function plot_time_series(container, title, data, series_keys, series_labels, series_colors, ylog) {
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

		// set color if custom colors were supplied
		if (series_colors != null) {
			series[i]['color'] = series_colors[i];
		}
	}

	var ymin = ylog ? 1 : 0;
	var ytype = ylog ? 'logarithmic' : 'linear'

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
				min: ymin,
				type: ytype,
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
				name: 'Actual HTTP 2.0 Support',
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
