var canvas_circle=document.getElementById("circleCanvas");
var context_circle=canvas_circle.getContext("2d");
context_circle.fillStyle="white";
context_circle.fillRect(0,0,canvas_circle.width,canvas_circle.height);
context_circle.fillStyle="black";

var interval = setInterval(newLine, 200);

var center = [canvas_circle.width/2, canvas_circle.height/2];
var r = canvas_circle.width/3;


function randomPoint() {
	theta = 2*Math.PI*Math.random();
	return [center[0] + Math.cos(theta)*r, center[1] + Math.sin(theta)*r];
}

function newLine() {
	s = randomPoint();
	e = randomPoint();
	context_circle.beginPath();
	context_circle.moveTo(s[0], s[1]);
	context_circle.lineTo(e[0], e[1]);
	context_circle.stroke();
}


