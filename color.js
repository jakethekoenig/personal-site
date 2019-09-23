var colorcanvas=document.getElementById("colorCanvas");
var color_ctx=colorcanvas.getContext("2d");

var n = 10;
var h = colorcanvas.height/n;
var w = colorcanvas.width/n;
var colors = ["#7FFF00", "#D2691E", "#FF8C00", "#FF8C00", "#1E90FF", "#ADFF2F"];

var interval = setInterval(newRect, 30);

function randInt(n) {
	return Math.floor(Math.random()*n);
}

function newRect() {
	var x = randInt(n);
	var y = randInt(n);
	var color = colors[randInt(colors.length)];
	color_ctx.fillStyle = color;
	color_ctx.fillRect(x*w, y*h, w, h);
}

