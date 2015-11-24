/* ========================= STORAGE ======================== */
/*
 * Wrapper for localStorage
 */
var LocalStorage = {
	set: function(key, value) {
		key = 'edu.cmu.cs.http2dashboard.' + key;
		localStorage[key] = JSON.stringify(value);
	},

	get: function(key) {
		key = 'edu.cmu.cs.http2dashboard.' + key;
		return localStorage[key] ? JSON.parse(localStorage[key]) : null;
	},

	exists: function(key) {
		key = 'edu.cmu.cs.http2dashboard.' + key;
		return localStorage[key] != null;
	},
};

/*
 * Wrapper for sessionStorage
 */
var SessionStorage = {
	set: function(key, value) {
		key = 'edu.cmu.cs.http2dashboard.' + key;
		sessionStorage[key] = JSON.stringify(value);
	},

	get: function(key) {
		key = 'edu.cmu.cs.http2dashboard.' + key;
		return sessionStorage[key] ? JSON.parse(sessionStorage[key]) : null;
	},

	exists: function(key) {
		key = 'edu.cmu.cs.http2dashboard.' + key;
		return sessionStorage[key] != null;
	},
};






/* ========================= MENUS ======================== */

/*
 * Fill menu with available crawl dates.
 * 	menu: the id of a ul element inside a bootstrap dropdown button
 *	data: array whose entries are dictionaries, each containing a "pretty_date" element
 *	change_callback: function to be called when user changes date;
 *		input to the function is the index in data the user picked
 */
function fill_date_menu(menu, data, change_callback) {
	for (i=0; i < data.length; i++) {
		crawl_date_menu = document.getElementById(menu);
		crawl_date_menu.innerHTML =
			crawl_date_menu.innerHTML
			+ '<li><a href="javascript: ' + change_callback + '(' + i + ');">' 
			+ data[i].pretty_date
			+ '</a></li>';
	}
}






/* ========================= PLOTTING ======================== */
var tag_labels = new Array();
tag_labels["telefonica-eth"] = "Barcelona, Spain";
tag_labels["telefonica-3G"] = "Barcelona, Spain (3G)";
tag_labels["telefonica-4G"] = "Barcelona, Spain (4G)";
tag_labels["cmu-eth"] = "Pittsburgh, USA";
tag_labels["case-eth"] = "Cleveland, USA";

var thresh_labels = new Array();
thresh_labels["h1"] = "H1";
thresh_labels["h2-1.0"] = "H2 (100%)";
thresh_labels["h2-0.9"] = "H2 (>90%)";
thresh_labels["h2-0.8"] = "H2 (>80%)";
thresh_labels["h2-0.5"] = "H2 (>50%)";
thresh_labels["h2-0.0"] = "H2 (>0%)";

// Build highcharts series entries
function build_series(series_keys, series_labels, data) {
	series = [];
	for (var i = 0; i < series_keys.length; i++) {
		var series_key = series_keys[i];
		series.push({
			name: series_labels[series_key],
			data: data[series_key]
			//data: data[series_key][data_key]
		});
	}

	return series;
}


function plot_cdf(container, data, title, xLabel, xMin, xMax, series_keys, series_labels, verb, value_suffix) {
	$(function () {
		$(container).highcharts({
			chart: {
				zoomType: 'x',
				type: 'line',
			},
			title: {
				text: title,
			},
			xAxis: {
				min: xMin,
				max: xMax,
				title: {
					text: xLabel,
				}
			},
			yAxis: {
				min: 0,
				max: 1,
				title: {
					text: 'CDF'
				}
			},
			tooltip: {
				shared: true,
				headerFormat: '',
				pointFormatter: function() {
					return '<span style="color:' + this.color + '">\u25CF</span> ' +
						this.series.name + ': <b>' + (this.y * 100).toFixed(2) + 
						'%</b> of sites ' + verb + ' <b>' + Math.round(this.x) + 
						'</b> or fewer ' + value_suffix + '<br>';
				},
			},
			legend: {
				enabled: true,
			},
			plotOptions: {
				line: {
					marker: {
						enabled: false,
					}
				},
			},

			series: build_series(series_keys, series_labels, data),
		});
	});

}

function plot_area_hist(container, data, title, xLabel, series_keys, series_labels, value_suffix) {
	$(function () {
		$(container).highcharts({
			chart: {
				zoomType: 'x',
				type: 'area',
			},
			title: {
				text: title,
			},
			xAxis: {
				title: {
					text: xLabel,
				}
			},
			yAxis: {
				min: 0,
				title: {
					text: 'Number of Sites',
				}
			},
			tooltip: {
				shared: true,
				headerFormat: '<span style="font-size: 10px">{point.key} ' + value_suffix + '</span><br/>',
				valueSuffix: ' sites',
			},
			legend: {
				enabled: true,
			},
			plotOptions: {
				area: {
					marker: {
						enabled: false,
					}
				},
			},

			series: build_series(series_keys, series_labels, data['series_data']),
		});
	});

}
