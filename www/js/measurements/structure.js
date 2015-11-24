---
---

$.getJSON('{{ site.baseurl }}/data/phase3.json', function(data) {
	fill_date_menu("structure-date-menu", data['num_objs'], "set_structure_crawl_date");
	set_structure_crawl_date(0);  // start with most recent crawl date
});

function set_structure_crawl_date(index) {
	$.getJSON('{{ site.baseurl }}/data/phase3.json', function(data) {

		// set display date
		display = document.getElementById("structure-date-display");
		display.innerHTML = data['num_objs'][index].pretty_date;
		
		plot_cdf('#num-obj-diff-cdf',
			data['num_objs'][index]['diff_cdfs'],
			'Number of Objects by Location and Network Type',
			'Reduction in Objects with H2 (# objects)',
			-20,
			20,
			['case-eth', 'cmu-eth', 'telefonica-eth', 'telefonica-4G', 'telefonica-3G'],
			tag_labels,
			'have', 'fewer objects with H2'
		);

		plot_cdf('#num-obj-threshold-cdf',
			data['num_objs'][index]['thresh_cdfs']['case-eth'],  // TODO: let viewer pick?
			'Number of Objects by Fraction of Objects Served with H2',
			'Number of Objects',
			0,
			250,
			['h2-1.0', 'h2-0.9', 'h2-0.8', 'h2-0.5', 'h2-0.0', 'h1'],
			thresh_labels,
			'have', 'objects'
		);
		
		plot_cdf('#num-conn-diff-cdf',
			data['num_conns'][index]['diff_cdfs'],
			'Number of Connections by Location and Network Type',
			'Reduction in Connections with H2 (# connections)',
			-5,
			35,
			['case-eth', 'cmu-eth', 'telefonica-eth', 'telefonica-4G', 'telefonica-3G'],
			tag_labels,
			'open', 'fewer connections with H2'
		);

		plot_cdf('#num-conn-threshold-cdf',
			data['num_conns'][index]['thresh_cdfs']['case-eth'],  // TODO: let viewer pick?
			'Number of Connections by Fraction of Objects Served with H2',
			'Number of Connections',
			0,
			100,
			['h2-1.0', 'h2-0.9', 'h2-0.8', 'h2-0.5', 'h2-0.0', 'h1'],
			thresh_labels,
			'open', 'connections'
		);
		
		plot_cdf('#num-domain-diff-cdf',
			data['num_domains'][index]['diff_cdfs'],
			'Number of Domains by Location and Network Type',
			'Reduction in Domains with H2 (# domains)',
			-3,
			3,
			['case-eth', 'cmu-eth', 'telefonica-eth', 'telefonica-4G', 'telefonica-3G'],
			tag_labels,
			'use', 'fewer domains with H2'
		);

		plot_cdf('#num-domain-threshold-cdf',
			data['num_domains'][index]['thresh_cdfs']['case-eth'],  // TODO: let viewer pick?
			'Number of Domains by Fraction of Objects Served with H2',
			'Number of Domains',
			0,
			50,
			['h2-1.0', 'h2-0.9', 'h2-0.8', 'h2-0.5', 'h2-0.0', 'h1'],
			thresh_labels,
			'use', 'domains'
		);
	});
}	
