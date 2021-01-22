var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
	coll[i].addEventListener("click", function() {
		this.classList.toggle("active");
		var content = this.nextElementSibling;
		if (content.classList.contains("open")) {
			this.innerHTML = this.innerHTML.slice(0,-4) + " [+]";
			content.classList.remove('open');
			content.classList.add('collapsed');
		} else {
			this.innerHTML = this.innerHTML.slice(0,-4) + " [-]";
			content.classList.add('open');
			content.classList.remove('collapsed');
		}
	});
}

var coll = document.getElementsByClassName("collapsed");
var i;

for (i = 0; i < coll.length; i++) {
	coll[i].addEventListener("click", function() {
		var title = this.previousElementSibling;
		if (this.classList.contains("collapsed")) {
			title.innerHTML = title.innerHTML.slice(0,-4) + " [-]";
			this.classList.add('open');
			this.classList.remove('collapsed');
		}
	});
}

