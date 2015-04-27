---
---

var proto_labels = new Array();
proto_labels["h1"] = "HTTP 1";
proto_labels["h2"] = "HTTP 2";
proto_labels["spdy"] = "SPDY";

$.getJSON('{{ site.baseurl }}/data/usage.json', function(data) {

	plot_area_hist('#num-obj-hist',
		data[0], // TODO: let user pick date
		'PDF',
		'Number of Objects',
		data[0]['protocols'],
		proto_labels,
		'num_objects',
		'objects');
	
	plot_cdf('#num-obj-cdf',
		data[0], // TODO: let user pick date
		'CDF',
		'Number of Objects',
		data[0]['protocols'],
		proto_labels,
		'num_objects',
		'have', 'objects');
	
	plot_area_hist('#num-conn-hist',
		data[0], // TODO: let user pick date
		'PDF',
		'Number of Connections',
		data[0]['protocols'],
		proto_labels,
		'num_connections',
		'connections');
	
	plot_cdf('#num-conn-cdf',
		data[0], // TODO: let user pick date
		'CDF',
		'Number of Connections',
		data[0]['protocols'],
		proto_labels,
		'num_connections',
		'open', 'connections');

	plot_area_hist('#num-domain-hist',
		data[0], // TODO: let user pick date
		'PDF',
		'Number of Domains',
		data[0]['protocols'],
		proto_labels,
		'num_domains',
		'domains');
	
	plot_cdf('#num-domain-cdf',
		data[0], // TODO: let user pick date
		'CDF',
		'Number of Domains',
		data[0]['protocols'],
		proto_labels,
		'num_domains',
		'use', 'domains');
	
});
