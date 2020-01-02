var c=document.getElementById("myCanvas");
var ctx=c.getContext("2d");

var atX = 0;
var atY = 0;
c.addEventListener('mousedown', this.down,false);
c.addEventListener('mouseup', this.up,false);
c.addEventListener('mousemove', this.move,false);
ctx.scale(1.5,1.5);
var interval = setInterval(redraw, 20);


function redraw() {
	ctx.clearRect(0, 0, c.width, c.height);
	ctx.fillStyle="white";
	ctx.fillRect(0,0,c.width,c.height);
	ctx.fillStyle="black";
	ctx.fillRect(atX,atY,5,5);
	ctx.stroke();
}

function down(e) {
	console.log(c.width+", "+c.height);
	down = true;
	atX = e.offsetX;
	atY = e.offsetY;
}

function move(e) {
	if (down) {
		atX = e.offsetX;
		atY = e.offsetY;
	}
}

function up(e) {
	down = false;
}
