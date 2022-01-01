function makeGithubPr() {
	var author = document.querySelector('.author_box').value;
	if (author==='') {
		author = "anon";
	}
	var authorEncoded = encodeURIComponent(author);
	var comment = document.querySelector('.comment_box').value;
	var commentEncoded = encodeURIComponent(comment);
	var comment_dir = document.querySelector('.submit_button').getAttribute('data-comment-dir');
	var filename = comment_dir + "/" + Math.floor(Math.random()*10000000);
	var message = `${author} made a comment`;
	var messageEncoded = encodeURIComponent(message);
	var value = `{\n\t"Author": "${author}",\n\t"Body": "${comment}"\n}`;
	var valueEncoded = encodeURIComponent(value);
	var url = `http://www.github.com/jakethekoenig/personal-site/new/master?filename=${filename}&value=${valueEncoded}&message=${messageEncoded}`

	window.open(url, '_blank');
}

document.querySelector('.submit_button').addEventListener("click", makeGithubPr);
