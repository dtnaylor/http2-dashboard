---
---
var proto_labels = new Array();
proto_labels["advertised_support_by_date"] = "Announced Support";
proto_labels["partial_support_by_date"] = "Partial Support";
proto_labels["true_support_by_date"] = "True Support";
proto_labels["spdy_2"] = "SPDY 2";
proto_labels["spdy_3"] = "SPDY 3";
proto_labels["spdy_3.1"] = "SPDY 3.1";
proto_labels["h2_advertised_support_by_date"] = "H2";
proto_labels["h2_14_advertised_support_by_date"] = "H2 Draft 14";
proto_labels["h2_15_advertised_support_by_date"] = "H2 Draft 15";
proto_labels["h2_17_advertised_support_by_date"] = "H2 Draft 17";
proto_labels["npn"] = "NPN";
proto_labels["alpn"] = "ALPN";
proto_labels["alpn-no-npn"] = "ALPN without NPN";
proto_labels["h2c-announce"] = "H2C (Announced)";
proto_labels["h2c-support"] = "H2C (True)";


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
		data['support_series_keys'],
		proto_labels,
		['#F0AD4E', '#5BC0DE', '#5CB85C'],
		false);
	
	plot_time_series('#draft-versions-chart',
		'Breakdown by Protocol Version (Announced Support)',
		data,
		data['protocol_series_keys'],
		proto_labels,
		 null,
		 false
		);
	
	plot_time_series('#aux-protocols-chart',
		'Auxiliary Protocols',
		data,
		data['aux_series_keys'],
		proto_labels,
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
			'Breakdown by Country (True Support)',
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

function plot_map(container, title, data) {
	$(function () {
		// Initiate the chart
		$(container).highcharts('Map', {

			title : {
				text : title
			},

			mapNavigation: {
				enabled: true,
				enableMouseWheelZoom: false,
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
