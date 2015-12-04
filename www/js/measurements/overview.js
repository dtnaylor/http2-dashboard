---
---


$.getJSON('{{ site.baseurl }}/data/summary.json', function(data) {

	var true_count = data['true_count'];
	var true_percent = true_count / 1000000.0 * 100;   // TODO: denom is not 1M
	true_progress_bar = document.getElementById('true-progress-bar');
	true_progress_bar.style.width = true_percent + '%';
	var true_msg = true_count.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + " sites <b>truly</b> support HTTP/2.";
	true_text = document.getElementById('true-text');
	true_text.innerHTML = true_msg;
	true_text_mobile = document.getElementById('true-text-mobile');
	true_text_mobile.innerHTML = true_msg;
	
	var partial_count = data['partial_count'];
	var partial_percent = partial_count / 1000000.0 * 100;   // TODO: denom is not 1M
	partial_progress_bar = document.getElementById('partial-progress-bar');
	partial_progress_bar.style.width = (partial_percent-true_percent) + '%';
	var partial_msg = partial_count.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + " sites <b>partially</b> support HTTP/2.";
	partial_text = document.getElementById('partial-text');
	partial_text.innerHTML = partial_msg;
	partial_text_mobile = document.getElementById('partial-text-mobile');
	partial_text_mobile.innerHTML = partial_msg;
	
	var announced_count = data['announced_count'];
	var announced_percent = announced_count / 1000000.0 * 100;   // TODO: denom is not 1M
	announced_progress_bar = document.getElementById('announced-progress-bar');
	announced_progress_bar.style.width = (announced_percent-partial_percent) + '%';
	var announced_msg = announced_count.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + " sites <b>announce</b> support for HTTP/2.";
	announced_text = document.getElementById('announced-text');
	announced_text.innerHTML = announced_msg;
	announced_text_mobile = document.getElementById('announced-text-mobile');
	announced_text_mobile.innerHTML = announced_msg;
});
