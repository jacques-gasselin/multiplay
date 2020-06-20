// global scope
let gameUUID = "00000000-0000-0000-0000-000000000000";
let connection = new MPBrowserConnection(gameUUID);
let localSession = null;

// update the messages every 15 seconds
window.setInterval(updateMessages, 15000);

function updateMessages() {
    let queryString = window.location.search;
    let urlParams = new URLSearchParams(queryString);
    if (urlParams.has('channel')) {
        let localSessionToken = urlParams.get('channel');
        if (localSessionToken) {
            localSession = connection.getLocalPlayer().getSessions().find(s => s.getSessionToken() == localSessionToken);
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
            messages.forEach(m => result = result + '<p>' + m.sender + ': ' + m.message + '</p>');
        }
        div.innerHTML = result;
    });
}

function updateChannels() {
    connection.getLocalPlayer().fetchSessions()
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
             + '<button class="button-small" onclick="leaveChannel(\'' + c.getSessionToken() +'\')">Leave</button>'
             + '</li>';
        });
        ul.innerHTML = result;
    });
}

function updateFriends() {
    let listPlayerFriendsUrl = connection.baseUrl + "listPlayerFriends.json?connection=" + connection.connectionToken + "&localPlayer=" + connection.getLocalPlayer().getLocalPlayerToken();
    fetch(listPlayerFriendsUrl)
    .then(response => response.json())
    .then(data => {
        let friends = data.friends;
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

function leaveChannel(c) {
    let url = connection.baseUrl + "leaveSession.json?connection=" + connection.connectionToken + "&localPlayer=" + connection.getLocalPlayer().localPlayerToken + "&session=" + c;
    fetch(url)
    .then(response => response.json())
    .then(data => {
        updateChannels();
    });
}

function addFriend() {
    let code = prompt("Enter friend code");
    let url = connection.baseUrl + "addPlayerFriend.json?connection=" + connection.connectionToken + "&localPlayer=" + connection.getLocalPlayer().getLocalPlayerToken() + "&friendCode=" + code
    fetch(url)
    .then(response => response.json())
    .then(data => {
        updateFriends();
    });
}

function encodeStringToBytes(s) {
    // FIXME use utf-8 conversion instead
	var bytes = [];
	for (var i = 0; i < s.length; i++) {
		bytes[i] = s.charCodeAt(i);
	}
	return new Uint8Array(bytes);
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
        let s = JSON.stringify(m);
        let data = encodeStringToBytes(s);
        let octets = new Blob(data, {type: "application/octet-stream"});
        let octetsGETParam = encodeURIComponent(s);
        let writeSessionsDataUrl = connection.baseUrl + "writeSessionData?connection=" + connection.connectionToken + "&session=" + localSession.getSessionToken() + "&data=" + octetsGETParam;
        fetch(writeSessionsDataUrl);
        updateMessages();
    });
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
    document.getElementById("message").addEventListener("keyup", keyOverrideEnterToSend);

    connection.connect().then(val => {
        connection.login().then(val => {
            let displayName = connection.getLocalPlayer().getDisplayName();
            let pname = document.getElementById("username");
            pname.innerHTML = "Signed in as " + displayName;

            let code = connection.getLocalPlayer().getFriendCode();
            let pcode = document.getElementById("friendcode");
            pcode.innerHTML = "Friend code : " + code;

            updateChannels();
            updateFriends();
            updateMessages();
        });
    });
}
