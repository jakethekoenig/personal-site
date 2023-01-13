
window.addEventListener("DOMContentLoaded", function() {
	Array.from(document.getElementsByClassName("filter_button")).forEach(function(e) {
		e.addEventListener("click", function() { filter(e); });
	});
});

function overlap(list1,list2) {
	var i;
	var j;
	for (i=0; i<list1.length; i++) {
		for (j=0; j<list2.length; j++) {
			if (list1[i] == list2[j] && list1[i]!="filter_button") {
				return true;
			}
		}
	}
	return false;
}

var last = [];

function filter(button) {
	var classes = button.classList
	var repeat = overlap(last, classes);
	if (!repeat) {
		last = classes;
	} else {
		last = [];
	}

	Array.from(document.getElementsByClassName("blogstub")).forEach(function(e) {
		if (!repeat && !overlap(classes, e.classList)) {
			e.parentElement.style.display = "none";
		} else {
			e.parentElement.style.display = "block";
		}
	});
}
