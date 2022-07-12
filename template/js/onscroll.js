var prevScrollpos = window.pageYOffset;
window.onscroll = function() {
  var currentScrollPos = window.pageYOffset;
  if (!/Mobi|Android/i.test(navigator.userAgent)) {
    // mobile!
	  return;
  }
  if (prevScrollpos > currentScrollPos) {
    sidem = document.getElementsByClassName("sidemenu");
	  if(sidem.length==1) {
		  sidem[0].style.top = "0px";
	  }
    nav = document.getElementsByClassName("topmenu")
	  if(nav.length==1) {
		  nav[0].style.top = "0px";
	  }
  } else {
	sidem = document.getElementsByClassName("sidemenu");
	  if(sidem.length==1) {
		  sidem[0].style.top = "-"+currentScrollPos+"px";
	  }
    nav = document.getElementsByClassName("topmenu")
	  if(nav.length==1) {
		  nav[0].style.top = "-"+currentScrollPos+"px";
	  }
  }
  prevScrollpos = currentScrollPos;
}
