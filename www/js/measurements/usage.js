---
---

var proto_labels = new Array();
proto_labels["h1"] = "HTTP 1";
proto_labels["h2"] = "HTTP 2";
proto_labels["spdy"] = "SPDY";

$.getJSON('{{ site.baseurl }}/data/usage.json', function(data) {
	fill_date_menu("usage-date-menu", data, "set_usage_crawl_date");
	set_usage_crawl_date(0);  // start with most recent crawl date
});

function set_usage_crawl_date(index) {
	$.getJSON('{{ site.baseurl }}/data/usage.json', function(data) {

		// set display date
		display = document.getElementById("usage-date-display");
		display.innerHTML = data[index].pretty_date;


		plot_area_hist('#num-obj-hist',
			data[index],
			'PDF',
			'Number of Objects',
			data[index]['protocols'],
			proto_labels,
			'num_objects',
			'objects');
		
		plot_cdf('#num-obj-cdf',
			data[index],
			'CDF',
			'Number of Objects',
			data[index]['protocols'],
			proto_labels,
			'num_objects',
			'have', 'objects');
		
		plot_area_hist('#num-conn-hist',
			data[index],
			'PDF',
			'Number of Connections',
			data[index]['protocols'],
			proto_labels,
			'num_connections',
			'connections');
		
		plot_cdf('#num-conn-cdf',
			data[index],
			'CDF',
			'Number of Connections',
			data[index]['protocols'],
			proto_labels,
			'num_connections',
			'open', 'connections');

		plot_area_hist('#num-domain-hist',
			data[index],
			'PDF',
			'Number of Domains',
			data[index]['protocols'],
			proto_labels,
			'num_domains',
			'domains');
		
		plot_cdf('#num-domain-cdf',
			data[index],
			'CDF',
			'Number of Domains',
			data[index]['protocols'],
			proto_labels,
			'num_domains',
			'use', 'domains');
	});
}	
