---
---
var tag_labels = new Array();
tag_labels["telefonica-eth"] = "Barcelona, Spain";
tag_labels["telefonica-3G"] = "Barcelona, Spain (3G)";
tag_labels["telefonica-4G"] = "Barcelona, Spain (4G)";
tag_labels["cmu-eth"] = "Pittsburgh, USA";
tag_labels["case-eth"] = "Cleveland, USA";

$.getJSON('{{ site.baseurl }}/data/phase3.json', function(data) {
	fill_date_menu("perf-date-menu", data['plt'], "set_perf_crawl_date");
	set_perf_crawl_date(0);  // start with most recent crawl date
});

function set_perf_crawl_date(index) {
	$.getJSON('{{ site.baseurl }}/data/phase3.json', function(data) {
		
		// set display date
		display = document.getElementById("perf-date-display");
		display.innerHTML = data['plt'][index].pretty_date;
		
		plot_cdf('#plt-cdf',
			data['plt'][index],
			'Page Load Time by Location and Network Type',
			'Page Load Time (ms)',
			-3000,
			3000,
			data['plt'][index]['series'],
			tag_labels,
			'loaded', 'milliseconds faster with H2');
		
	});
}
