// global scope
let gameUUID = "00000000-0000-0000-0000-000000000000";
let connection = new MPBrowserConnection(gameUUID);
let localSession = null;

// update the messages every 15 seconds
window.setInterval(updateMessages, 15000);

function updateMessages() {
    var player = connection.getLocalPlayer();

    let queryString = window.location.search;
    let urlParams = new URLSearchParams(queryString);
    if (urlParams.has('channel')) {
        let localSessionToken = urlParams.get('channel');
        if (localSessionToken) {
            localSession = player.getSessions().find(s => s.getSessionToken() == localSessionToken);
        }
    }

    if (!localSession) {
        return;
    }

    localSession.fetchDataAsJSON()
    .then(data => {
        var messages = data.messages;
        let div = document.getElementById("messages");
        result = '';
        if (messages) {
            var lastSender = "";
            var isMe = false;
            var pTag = '<p>';
            messages.forEach(m => {
                if (lastSender != m.sender) {
                    lastSender = m.sender;
                    isMe = (m.sender == player.getDisplayName());
                    pTag = isMe ? '<p style="text-align:right">' : '<p>'
                    result = result + '<br/>' + pTag + '<i class="player-name">' + m.sender + '</i></p>'
                }
                if (isMe) {
                    result = result + pTag + m.message + '&nbsp;</p>';
                }
                else {
                    result = result + pTag + '&nbsp;' + m.message + '</p>';
                }
            });
        }
        div.innerHTML = result;
    });
}

function updateChannels() {
    var player = connection.getLocalPlayer();
    player.fetchSessions()
    .then(channels => {
        if (!localSession && channels) {
            localSession = channels[0];
            updateMessages();
        }
        let ul = document.getElementById("channels");
        result = '';
        let chatUrl = connection.baseUrl + "application/chat.html?channel=";
        channels.forEach(c => {
            result = result
             + '<li>' + c.getShareCode() + ':<a class="item" href="' + chatUrl + c.getSessionToken() + '">'+ c.getDisplayName() + '</a>'
             + '<button class="button-leave" onclick="leaveChannel(\'' + c.getSessionToken() +'\')">&#x2796;</button>'
             + '</li>';
        });
        ul.innerHTML = result;
    });
}

function updateFriends() {
    connection.getLocalPlayer().fetchFriends()
    .then(friends => {
        let ul = document.getElementById("friends");
        result = '';
        friends.forEach(f => result = result + '<li><a href="' + chatUrl + f.remotePlayerToken + '">' + f.displayName + '</li>');
        ul.innerHTML = result;
    });
}

function createChannel() {
    let name = prompt("Channel name")
    connection.getLocalPlayer().createSessionWithName(name)
    .then(newChannel => {
        // FIXME the new channel is returned, just update the UI incrementally
        updateChannels();
        updateMessages();
    });
}

function joinChannel() {
    let code = prompt("Enter channel share code");
    connection.getLocalPlayer().joinSessionByShareCode(code)
    .then(newChannel => {
        // FIXME the new channel is returned, just update the UI incrementally
        updateChannels();
        updateMessages();
    });
}

function leaveChannel(localSessionToken) {
    let session = connection.getLocalPlayer().getSessions().find(s => s.getSessionToken() == localSessionToken);
    connection.getLocalPlayer().leaveSession(session)
    .then(data => {
        updateChannels();
    });
}

function addFriend() {
    let code = prompt("Enter friend code");
    connection.getLocalPlayer().addFriendWithCode(code)
    .then(data => {
        updateFriends();
    });
}

function send() {
    if (!localSession) {
        return;
    }
    localSession.fetchDataAsJSON()
    .then(oldData => {
        let oldMessages = [];
        if (oldData.messages) {
            oldMessages = oldData.messages;
        }
        // append form text as a message and write the data back
        let textField = document.getElementById("message");
        let newMessages = [{ 'sender' : connection.getLocalPlayer().getDisplayName(), 'message' : textField.value}];
        textField.value = "";

        let m = { 'messages' : oldMessages.concat(newMessages) };

        localSession.sendObjectAsJSONData(m).
        then(data => {
            updateMessages();
        });
    });
}

function updatePlayer(localPlayer) {
    let displayName = localPlayer.getDisplayName();
    let pname = document.getElementById("username");
    let user = document.getElementById("user");
    let sbutton = document.getElementById("sign-in-button");
    let nbutton = document.getElementById("change-name-button");
    if (localPlayer.isAuthenticated()) {
        pname.innerHTML = "Signed in as " + displayName;
        sbutton.style.display = "none";
        nbutton.style.display = "block";
        user.style.gridTemplateColumns = "auto 100px auto";
    }
    else {
        pname.innerHTML = "Guest account " + displayName;
        sbutton.style.display = "block";
        nbutton.style.display = "none";
        user.style.gridTemplateColumns = "80px auto auto";
    }

    let code = localPlayer.getFriendCode();
    let pcode = document.getElementById("friendcode");
    pcode.innerHTML = "Friend code : " + code;
}

function signIn() {
    connection.getLocalPlayer().httpAuthenticate()
    .then(localPlayer => {
        updatePlayer(localPlayer);
    });
}

function changeName() {
    let name = prompt("New display name")
    connection.getLocalPlayer().setDisplayName(name);
    updatePlayer(connection.getLocalPlayer());
    updateMessages();
}

function keyOverrideEnterToSend(event) {
    if (event.keyCode === 13) {
        event.preventDefault();
        send();
    }
}

function load() {
    // override 'Enter' to send.
    document.getElementById("message").addEventListener("keyup", keyOverrideEnterToSend);

    connection.connect().then(val => {
        connection.login().then(localPlayer => {
            updatePlayer(localPlayer);
            updateChannels();
            updateFriends();
            updateMessages();
        });
    });
}
