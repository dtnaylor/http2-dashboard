---
---
var proto_labels = new Array();
proto_labels["h1"] = "HTTP 1";
proto_labels["h2"] = "HTTP 2";
proto_labels["spdy"] = "SPDY";

$.getJSON('{{ site.baseurl }}/data/usage.json', function(data) {
	
	plot_area_hist('#plt-hist',
		data[0], // TODO: let user pick date
		'PDF',
		'Page Load Time',
		data[0]['protocols'],
		proto_labels,
		'plt',
		'seconds');

	plot_cdf('#plt-cdf',
		data[0], // TODO: let user pick date
		'CDF',
		'Page Load Time',
		data[0]['protocols'],
		proto_labels,
		'plt',
		'took', 'seconds');
	
});
