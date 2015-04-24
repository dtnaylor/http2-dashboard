---
---
var proto_labels = new Array();
proto_labels["h1"] = "HTTP 1";
proto_labels["h2"] = "HTTP 2";
proto_labels["spdy"] = "SPDY";

$.getJSON('{{ site.baseurl }}/data/usage.json', function(data) {

	plot_cdf('#num-obj-cdf',
		'Number of Objects',
		data[0], // TODO: let user pick date
		data[0]['protocols'],
		proto_labels,
		'num_objects',
		'have', 'objects');
	
	plot_cdf('#num-conn-cdf',
		'Number of Connections',
		data[0], // TODO: let user pick date
		data[0]['protocols'],
		proto_labels,
		'num_connections',
		'open', 'connections');

	plot_cdf('#num-domain-cdf',
		'Number of Domains',
		data[0], // TODO: let user pick date
		data[0]['protocols'],
		proto_labels,
		'num_domains',
		'use', 'domains');
	
});
