// credits to https://dev.to/nyxtom/drawing-interactive-graphs-with-canvas-and-javascript-o1j
const canvas = document.querySelector('canvas');
const context = canvas.getContext('2d');

var NODE_RAD = 20;
var nodes = [];

function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

window.onresize = resize;
resize();

function drawNode(node) {
    context.beginPath();
    context.fillStyle = node.fillStyle;
    context.arc(node.x, node.y, node.radius, 0, Math.PI * 2, true);
    context.strokeStyle = node.strokeStyle;
    context.stroke();
    context.fill();
}

var selection = undefined;

function within(x, y) {
    return nodes.find(n => {
        return x > (n.x - n.radius) && 
            y > (n.y - n.radius) &&
            x < (n.x + n.radius) &&
            y < (n.y + n.radius);
    });
}

function move(e) {
    if (selection && e.buttons) {
        selection.x = e.x;
        selection.y = e.y;
        draw();
    }
}

Array.prototype.handle = function(obj) {
    item_src = JSON.stringify(obj.from)
    item_dst = JSON.stringify(obj.to)
    var i = this.length;
    while (i--) {
        iter_src = JSON.stringify(this[i].from)
        iter_dst = JSON.stringify(this[i].to)
        if ((item_src === iter_src && item_dst === iter_dst) || (item_src === iter_dst && item_dst === iter_src)) {
            this.splice(i, 1)
            return false
        }
    }
    this.push(obj);
    return true
}


function down(e) {
    let target = within(e.x, e.y);
    if (selection && selection.selected) {
        selection.selected = false;
    }
    if (target) {
        let should_select = true;
        if (selection && selection !== target) {
            let item = { from: selection, to: target }
            should_select = edges.handle(item);
        }
        selection = target;
        selection.selected = should_select;
        draw();
    }
}

function up(e) {
    if (!selection) {
        let node = {
            x: e.x,
            y: e.y,
            radius: NODE_RAD,
            fillStyle: '#22cccc',
            strokeStyle: '#009999',
            selectedFill: '#88aaaa',
            selected: false
        };
        nodes.push(node);
        draw();
    }
    if (selection && !selection.selected) {
        selection = undefined;
    }
    draw();
}

var edges = [];

function canvas_arrow(context, fromx, fromy, tox, toy) {
    var headlen = 30; // length of head in pixels
    var head_angle = 12;
    var dx = tox - fromx;
    var dy = toy - fromy;
    var angle = Math.atan2(dy, dx);
    context.beginPath();
    context.moveTo(fromx, fromy);
    context.lineTo(tox - NODE_RAD*Math.cos(angle), toy-NODE_RAD*Math.sin(angle));
    context.stroke();
    context.beginPath();
    context.lineTo(tox - headlen * Math.cos(angle - Math.PI / head_angle), toy - headlen * Math.sin(angle - Math.PI / head_angle));
    context.lineTo(tox - NODE_RAD*Math.cos(angle), toy-NODE_RAD*Math.sin(angle));
    context.lineTo(tox - headlen * Math.cos(angle + Math.PI / head_angle), toy - headlen * Math.sin(angle + Math.PI / head_angle));
    context.fill();
  }
  
function draw() {
    context.clearRect(0, 0, window.innerWidth, window.innerHeight);
    context.fillStyle = '#22cccc'
    for (let i = 0; i < edges.length; i++) {
        let fromNode = edges[i].from;
        let toNode = edges[i].to;
        canvas_arrow(context, fromNode.x, fromNode.y, toNode.x, toNode.y);
    }

    for (let i = 0; i < nodes.length; i++) {
        let node = nodes[i];
        context.beginPath();
        context.fillStyle = node.selected ? node.selectedFill : node.fillStyle;
        context.arc(node.x, node.y, node.radius, 0, Math.PI * 2, true);
        context.strokeStyle = node.strokeStyle;
        context.fill();
        context.fillStyle = 'black';
        context.textAlign = 'center';
        context.font = '30px serif';
        context.fillText(i+1, node.x, node.y+NODE_RAD/2)
        context.stroke();
    }
}

window.onmousemove = move;
window.onmousedown = down;
window.onmouseup = up;


