// global scope
let gameUUID = "00000000-0000-0000-0000-000000000001";
let connection = new MPBrowserConnection(gameUUID);

var sessions = [];

var localPlayer = null;

var canvas = null;

class Board {
    constructor() {
        this.points = [
            0, 0, 0,
            0, 0, 0,
            0, 0, 0
        ];
    }
}

class Game {
    constructor(session) {
        this.session = session;
        this.board = new Board();
        this.playerIsX = true;
    }
}

var game = new Game(null);

function updatePlayer(player) {
    localPlayer = player;
    window.requestAnimationFrame(draw);
}

function updateGameSessions() {

}

function mouseDown(event) {
    let x = event.offsetX;
    let y = event.offsetY;

    let cellSize = canvas.width / 3;

    let j = Math.floor(y / cellSize);
    let i = Math.floor(x / cellSize);

    let index = j * 3 + i;

    let points = game.board.points;

    if (points[index] == 0) {
        points[index] = game.playerIsX ? 1 : 2;
        game.playerIsX = !game.playerIsX;
        requestAnimationFrame(draw);
    }
}

function keyDown(event) {

}

function keyUp(event) {

}

function drawBoard(g, board, x, y, width, height) {
    g.beginPath();
    g.moveTo(width / 3, 0);
    g.lineTo(width / 3, height);
    g.moveTo(2 * width / 3, 0);
    g.lineTo(2 * width / 3, height);

    g.moveTo(0, height / 3);
    g.lineTo(width, height / 3);
    g.moveTo(0, 2 * height / 3);
    g.lineTo(width, 2 * height / 3);

    g.stroke();

    let cellSize = width / 3;

    for (var j = 0; j < 3; ++j) {
        for (var i = 0; i < 3; ++i) {
            if (board.points[j * 3 + i] == 1) {
                g.beginPath();
                g.moveTo(i * cellSize + 3, j * cellSize + 3);
                g.lineTo((i + 1) * cellSize - 3, (j + 1) * cellSize - 3);
                g.moveTo((i + 1) * cellSize - 3, j * cellSize + 3)
                g.lineTo(i * cellSize + 3, (j + 1) * cellSize - 3);
                g.stroke();
            }
            else if (board.points[j * 3 + i] == 2) {
                g.beginPath();
                g.arc(i * cellSize + cellSize / 2, j * cellSize + cellSize / 2, cellSize / 2 - 4, 0, 2 * Math.PI, true);
                g.stroke();
            }
        }
    }
}

function draw(timestamp) {
    let title = document.getElementById("gameTitle");
    let playerName = (localPlayer != null) ? localPlayer.getDisplayName() : "Player";
    title.innerHTML = game.playerIsX ?
        "<b>" + playerName + "</b> vs Opponent" :
        "" + playerName + " vs <b>Opponent</b>";

    let g = canvas.getContext("2d");

    let width = canvas.width;
    let height = canvas.height;

    g.clearRect(0, 0, width, height);

    drawBoard(g, game.board, 0, 0, width, height);
}

function load() {
    canvas = document.getElementById("gameCanvas");

    canvas.addEventListener("mousedown", mouseDown);
    canvas.addEventListener("keydown", keyDown);
    canvas.addEventListener("keyup", keyUp);

    connection.connect().then(val => {
        connection.login().then(player => {
            updatePlayer(player);
            updateGameSessions();
        });
    });

    window.requestAnimationFrame(draw);
}
