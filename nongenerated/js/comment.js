function makeGithubPr() {
	var author = JSON.stringify(escapeHtml(document.querySelector('.author_box').value));
	if (author==='') {
		author = "anon";
	}
	var authorEncoded = encodeURIComponent(author);
	var comment = JSON.stringify(escapeHtml(document.querySelector('.comment_box').value));
	var commentEncoded = encodeURIComponent(comment);
	var comment_dir = document.querySelector('.submit_button').getAttribute('data-comment-dir');
	var filename = "comments/" + comment_dir + "/" + Math.floor(Math.random()*10000000) + ".json";
	var message = `${author} made a comment`;
	var messageEncoded = encodeURIComponent(message);
	var href = window.location.href;
	var loc = encodeURIComponent(href.substring(href.indexOf("com")+3));
	var date = Date.now();
	var value = `{\n\t"Author": ${author},\n\t"Body": ${comment},\n\t"Page": ${loc},\n\t"time": ${date}\n}`;
	var valueEncoded = encodeURIComponent(value);
	var url = `http://www.github.com/jakethekoenig/personal-site/new/master?filename=${filename}&value=${valueEncoded}&message=${messageEncoded}`

	window.open(url, '_blank');
}

function escapeHtml(unsafe)
{
	return unsafe
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;")
		.replace(/'/g, "&#039;");
}


document.querySelector('.submit_button').addEventListener("click", makeGithubPr);
