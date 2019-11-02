var c_puddle=document.getElementById("puddleCanvas");
var ctx_puddle=c_puddle.getContext("2d");

var radius_speed = 2;
var spawn_rate_puddle= 25;
var rate_puddle = 20;
var offset_puddle = 0;
var H = 400;
var W = 400;
drops = [];

var interval = setInterval(puddle_update, rate_puddle);

function puddle_update() {
	puddle_physics();
	puddle_redraw();
}

function puddle_redraw() {
	ctx_puddle.clearRect(0, 0, c.width, c.height);
	drops.forEach(function(e) {
		ctx_puddle.beginPath();
		ctx_puddle.arc(e.x,e.y,e.radius, 0, 2*Math.PI);
		ctx_puddle.stroke();
	});
}

function puddle_physics() {
	drops.forEach(function(e) {
		e.radius += radius_speed;
	});
	drops.filter(drop => drop.radius < 900);
	offset_puddle += 1;
	if (offset_puddle >spawn_rate_puddle) {
		offset_puddle -= spawn_rate_puddle;
		drops.push({radius: 1, x:W*Math.random(), y:H*Math.random()});
	}
}
