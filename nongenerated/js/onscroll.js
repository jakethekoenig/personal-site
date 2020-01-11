var prevScrollpos = window.pageYOffset;
window.onscroll = function() {
  var currentScrollPos = window.pageYOffset;
  if (window.innerWidth>620) {
	  return;
  }
  if (prevScrollpos > currentScrollPos || currentScrollPos<100) {
    sidem = document.getElementsByClassName("sidemenu");
	  if(sidem.length==1) {
		  sidem[0].style.top = "-50px";
	  }
    nav = document.getElementsByClassName("navigation")
	  if(nav.length==1) {
		  nav[0].style.top = "150px";
	  }
  } else {
	sidem = document.getElementsByClassName("sidemenu");
	  if(sidem.length==1) {
		  sidem[0].style.top = "-350px";
	  }
    nav = document.getElementsByClassName("navigation")
	  if(nav.length==1) {
		  nav[0].style.top = "-350px";
	  }
  }
  prevScrollpos = currentScrollPos;
}
