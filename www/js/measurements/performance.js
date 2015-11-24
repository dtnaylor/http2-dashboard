---
---

$.getJSON('{{ site.baseurl }}/data/phase3.json', function(data) {
	fill_date_menu("perf-date-menu", data['plt'], "set_perf_crawl_date");
	set_perf_crawl_date(0);  // start with most recent crawl date
});

function set_perf_crawl_date(index) {
	$.getJSON('{{ site.baseurl }}/data/phase3.json', function(data) {
		
		// set display date
		display = document.getElementById("perf-date-display");
		display.innerHTML = data['plt'][index].pretty_date;
		
		plot_cdf('#plt-diff-cdf',
			data['plt'][index]['diff_cdfs'],
			'Page Load Time by Location and Network Type',
			'Reduction in Load Time with H2 (ms)',
			-3000,
			3000,
			['case-eth', 'cmu-eth', 'telefonica-eth', 'telefonica-4G', 'telefonica-3G'],
			tag_labels,
			'loaded', 'milliseconds faster with H2'
		);

		plot_cdf('#plt-threshold-cdf',
			data['plt'][index]['thresh_cdfs']['case-eth'],  // TODO: let viewer pick?
			'Page Load Time by Fraction of Objects Served with H2',
			'Page Load Time (ms)',
			0,
			10000,
			['h2-1.0', 'h2-0.9', 'h2-0.8', 'h2-0.5', 'h2-0.0', 'h1'],
			thresh_labels,
			'loaded', 'milliseconds faster with H2'
		);
		
	});
}
