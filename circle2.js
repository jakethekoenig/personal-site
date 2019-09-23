var canvas_circle2=document.getElementById("circle2");
var ctx_circle2=canvas_circle2.getContext("2d");
ctx_circle2.fillStyle="white";
ctx_circle2.fillRect(0,0,c.width,c.height);
ctx_circle2.fillStyle="black";

var interval = setInterval(newLine, 200);

var center = [canvas_circle2.width/2, canvas_circle2.height/2];
var r = canvas_circle2.width/3;
var at = 0;

function point(theta) {
	return [center[0] + Math.cos(theta)*r, center[1] + Math.sin(theta)*r];
}

function next() {
	return at + Math.PI*Math.random();
}

function newLine() {
	s = point(at);
	at = next();
	e = point(at);
	ctx_circle2.beginPath();
	ctx_circle2.moveTo(s[0], s[1]);
	ctx_circle2.lineTo(e[0], e[1]);
	ctx_circle2.stroke();
}


