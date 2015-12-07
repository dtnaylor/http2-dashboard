---
---
var series_labels = new Array();
series_labels["alexa_db_size"] = "URL List Size";

$.getJSON('{{ site.baseurl }}/data/alexa_db_size.json', function(data) {
	plot_time_series('#alexa-db-evolution-chart',
		'Number of Sites Probed',
		data,
		['alexa_db_size'],
		series_labels,
		null,
		false);
});
