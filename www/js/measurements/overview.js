---
---


$.getJSON('{{ site.baseurl }}/data/summary.json', function(data) {
	var announced_count = data['announced_count'];
	var announced_percent = announced_count / 1000000.0 * 100;
	announced_progress_bar = document.getElementById('announced-progress-bar');
	announced_progress_bar.style.width = announced_percent + '%';
	announced_progress_bar.classList.add(bar_color(announced_percent));
	announced_text = document.getElementById('announced-text');
	announced_text.innerHTML = announced_count.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + " of the Alexa top 1 million sites <b>announce</b> support for HTTP/2."
	
	var actual_count = data['actual_count'];
	var actual_percent = actual_count / 1000000.0 * 100;
	actual_progress_bar = document.getElementById('actual-progress-bar');
	actual_progress_bar.style.width = actual_percent + '%';
	actual_progress_bar.classList.add(bar_color(actual_percent));
	actual_text = document.getElementById('actual-text');
	actual_text.innerHTML = actual_count.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + " of the Alexa top 1 million sites <b>actually</b> support HTTP/2.<br>&nbsp;"
});


function bar_color(percentage) {
	if (percentage < 10)
		return 'progress-bar-danger';
	else if (percentage < 50)
		return 'progress-bar-warning';
	else
		return 'progress-bar-success';
}
