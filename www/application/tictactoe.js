// global scope
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
    constructor(name) {
        this.name = name;
        this.board = new Board();
        this.playerIsX = true;
    }

    isRangeAWinForPlayer(player, startIndex, step) {
        if (player == 0) {
            return false;
        }
        for (var i = 0; i < 3; ++i) {
            let index = startIndex + i * step;
            if (this.board.points[index] != player) {
                return false;
            }
        }
        return true;
    }

    didPlayerWin(player) {
        // each row
        for (var row = 0; row < 3; ++row) {
            if (this.isRangeAWinForPlayer(player, row * 3, 1)) {
                return true;
            }
        }
        // each column
        for (var col = 0; col < 3; ++col) {
            if (this.isRangeAWinForPlayer(player, col, 3)) {
                return true;
            }
        }
        // each diagonal
        if (this.isRangeAWinForPlayer(player, 0, 4)) {
            return true;
        }
        if (this.isRangeAWinForPlayer(player, 2, 2)) {
            return true;
        }
        return false;
    }

    isTied() {
        for (var p in this.board.points) {
            if (p == 0) {
                return false;
            }
        }
        return true;
    }

    isGameOver() {
        if (this.didPlayerWin(1)) {
            return true;
        }
        if (this.didPlayerWin(2)) {
            return true;
        }
        return this.isTied();
    }
}

var currentGame = new Game("Default");

/// ----- Multiplay and UI code
let gameUUID = "00000000-0000-0000-0000-000000000001";
let connection = new MPBrowserConnection(gameUUID);

var currentSession = null;
var localPlayer = null;

function loginPressed() {
    localPlayer.httpAuthenticate()
    .then(player => {
        updatePlayer(player);
    });
}

function newGamePressed() {
    let name = prompt("Game name")
    connection.getLocalPlayer().createSessionWithName(name)
    .then(s => {
        updateGameSessions();
        currentSession = s;
        updateGameForSession(s);
    });
}

function updateGameSessions() {
    localPlayer.fetchSessions()
    .then(gameSessions => {
        sessions = gameSessions;
        if (!currentSession && gameSessions) {
            currentSession = gameSessions[0];
            updateGameForSession(currentSession);
        }
        let ul = document.getElementById("gamesList");
        result = '';
        gameSessions.forEach(s => {
            result = result
             + '<li>'
             + s.getDisplayName()
             + '&nbsp;'
             + '<button onclick="selectGameBySessionToken(\'' + s.getSessionToken() +'\')"> -> </button>'
             + '</li>';
        });
        ul.innerHTML = result;
    });
}

function selectGameBySessionToken(sessionToken) {
    localPlayer.getSessions().forEach(s => {
        if (s.getSessionToken() == sessionToken) {
            currentSession = s;
            updateGameForSession(s);
        }
    });
}

function updateGameForSession(session) {
    session.fetchDataAsJSON().then(data => {
        var game = new Game(session.getDisplayName());
        if (data.board) {
            game.board.points = data.board.points;
            game.playerIsX = data.playerIsX;
        }
        currentGame = game;
        requestAnimationFrame(draw);
    });
}

function updateCurrentSession() {
    updateGameForSession(currentSession);
}

window.setInterval(updateCurrentSession, 15000);

/// ----- Game Code

var canvas = null;

function updatePlayer(player) {
    localPlayer = player;

    let displayName = localPlayer.getDisplayName();
    let pname = document.getElementById("playerName");
    if (localPlayer.isAuthenticated()) {
        pname.innerHTML = 'Signed in as ' + displayName;
    }
    else {
        pname.innerHTML = '<button onclick="loginPressed()">Login</button> Guest user ' + displayName;
    }

    window.requestAnimationFrame(draw);
}

function makeMoveAtIndex(index) {
    if (currentGame.isGameOver()) {
        return;
    }

    let points = currentGame.board.points;

    if (points[index] == 0) {
        points[index] = currentGame.playerIsX ? 1 : 2;
        currentGame.playerIsX = !currentGame.playerIsX;
        currentSession.sendObjectAsJSONData(currentGame);

        requestAnimationFrame(draw);
    }
}

function mouseDown(event) {
    let x = event.offsetX;
    let y = event.offsetY;

    let cellSize = canvas.width / 3;

    let j = Math.floor(y / cellSize);
    let i = Math.floor(x / cellSize);

    let index = j * 3 + i;

    makeMoveAtIndex(index);
}

function keyDown(event) {

}

function keyUp(event) {

}

function drawBoard(g, game, x, y, width, height) {
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
            if (game.board.points[j * 3 + i] == 1) {
                g.beginPath();
                g.moveTo(i * cellSize + 3, j * cellSize + 3);
                g.lineTo((i + 1) * cellSize - 3, (j + 1) * cellSize - 3);
                g.moveTo((i + 1) * cellSize - 3, j * cellSize + 3)
                g.lineTo(i * cellSize + 3, (j + 1) * cellSize - 3);
                g.stroke();
            }
            else if (game.board.points[j * 3 + i] == 2) {
                g.beginPath();
                g.arc(i * cellSize + cellSize / 2, j * cellSize + cellSize / 2, cellSize / 2 - 4, 0, 2 * Math.PI, true);
                g.stroke();
            }
        }
    }

    // draw winning strikethroughs

    for (var player = 1; player <= 2; ++player) {
        for (var row = 0; row < 3; ++row) {
            if (game.isRangeAWinForPlayer(player, row * 3, 1)) {
                g.beginPath();
                g.moveTo(0, row * cellSize + cellSize / 2);
                g.lineTo(3 * cellSize, row * cellSize + cellSize / 2);
                g.stroke();
            }
        }
        for (var col = 0; col < 3; ++col) {
            if (game.isRangeAWinForPlayer(player, col, 3)) {
                g.beginPath();
                g.moveTo(col * cellSize + cellSize / 2, 0);
                g.lineTo(col * cellSize + cellSize / 2, 3 * cellSize);
                g.stroke();
            }
        }

        if (game.isRangeAWinForPlayer(player, 0, 4)) {
            g.beginPath();
            g.moveTo(0, 0);
            g.lineTo(width, height);
            g.stroke();
        }

        if (game.isRangeAWinForPlayer(player, 2, 2)) {
            g.beginPath();
            g.moveTo(width, 0);
            g.lineTo(0, height);
            g.stroke();
        }
    }



}

function draw(timestamp) {
    let title = document.getElementById("gameTitle");
    let playerName = (localPlayer != null) ? localPlayer.getDisplayName() : "Player";
    title.innerHTML = currentGame.playerIsX ?
        currentGame.name + ": <b>" + playerName + "</b> vs Opponent" :
        currentGame.name + ": " + playerName + " vs <b>Opponent</b>";

    let g = canvas.getContext("2d");

    let width = canvas.width;
    let height = canvas.height;

    g.clearRect(0, 0, width, height);

    drawBoard(g, currentGame, 0, 0, width, height);
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
