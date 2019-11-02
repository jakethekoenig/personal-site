var squareCanvas=document.getElementById("squareCanvas");
var square_ctx=squareCanvas.getContext("2d");

spawn_rate = 7;
offset = 0;
max_speed = 10;
max_size = 200;
var squares = [];

var interval = setInterval(update, 20);

function update() {
	physics();
	redraw();
}

function physics() {
	if (offset>spawn_rate) {
		offset -= spawn_rate;
		squares.push({speed: max_speed*Math.random(), height: max_size*Math.random(), width: max_size*Math.random(), x: -max_size-10, y: -max_size+(max_size+squareCanvas.height)*Math.random()});
	}
	squares.forEach(function(e) {
		e.x += e.speed;
	});
	squares.filter(s => s.x>squareCanvas.width);	
	offset+=1;
}

function redraw() {
	square_ctx.clearRect(0, 0, squareCanvas.width, squareCanvas.height);
	squares.forEach(function(e) {
		square_ctx.beginPath();
		square_ctx.rect(e.x,e.y,e.width, e.height);
		square_ctx.stroke();
	});
}

