---
---
var proto_labels = new Array();
proto_labels["h1"] = "HTTP 1";
proto_labels["h2"] = "HTTP 2";
proto_labels["spdy"] = "SPDY";

$.getJSON('{{ site.baseurl }}/data/usage.json', function(data) {
	fill_date_menu("perf-date-menu", data, "set_perf_crawl_date");
	set_perf_crawl_date(0);  // start with most recent crawl date
});

function set_perf_crawl_date(index) {
	$.getJSON('{{ site.baseurl }}/data/usage.json', function(data) {
		
		// set display date
		display = document.getElementById("perf-date-display");
		display.innerHTML = data[index].pretty_date;
		
		plot_area_hist('#plt-hist',
			data[index],
			'PDF',
			'Page Load Time',
			data[index]['protocols'],
			proto_labels,
			'plt',
			'seconds');

		plot_cdf('#plt-cdf',
			data[index],
			'CDF',
			'Page Load Time',
			data[index]['protocols'],
			proto_labels,
			'plt',
			'took', 'seconds');
		
	});
}
