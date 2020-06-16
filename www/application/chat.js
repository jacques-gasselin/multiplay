let baseUrl = window.location.protocol + '//' + window.location.hostname + ':12345/';
// global scope
let gameUUID = "00000000-0000-0000-0000-000000000000";
// FIXME, get the device UUID from a session token
let deviceUUID = "00000000-0000-0000-0000-000000000000";
let connection = "";
let localPlayer = "";
let localSession = "";
let displayName = "";

let createSessionUrl = baseUrl + "createSession.json";

function updateMessages() {
    if (!localSession) {
        return;
    }
    let readSessionsDataUrl = baseUrl + "readSessionData?connection=" + connection + "&session=" + localSession;
    fetch(readSessionsDataUrl)
    .then(response => response.blob())
    .then(blob => readBlobAsync(blob))
    .then(blobText => {
        if (blobText) {
            var messages = []
            try {
                let data = JSON.parse(blobText);
                messages = data.messages;
            }
            catch(err) {
                console.log(err.message);
            }
            let div = document.getElementById("messages");
            result = '';
            if (messages) {
                messages.forEach(m => result = result + '<p>' + m.sender + ': ' + m.message + '</p>');
            }
            div.innerHTML = result;
        }
    });
}

function updateChannels() {
    let listPlayerSessionsUrl = baseUrl + "listPlayerSessions.json?connection=" + connection + "&localPlayer=" + localPlayer;
    fetch(listPlayerSessionsUrl)
    .then(response => response.json())
    .then(data => {
        let channels = data.sessions;
        if (!localSession && channels) {
            localSession = channels[0].localSessionToken;
            updateMessages();
        }
        let ul = document.getElementById("channels");
        result = '';
        let chatUrl = baseUrl + "chat.html?channel=";
        channels.forEach(c => result = result + '<li><a href="' + chatUrl + c.localSessionToken + '">' + c.displayName + '</li>');
        ul.innerHTML = result;
    });
}

function updateFriends() {
    let listPlayerFriendsUrl = baseUrl + "listPlayerFriends.json?connection=" + connection + "&localPlayer=" + localPlayer;
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
    let url = createSessionUrl + '&displayName=' + encodeURIComponent(name)
    fetch(url)
    .then(response => response.json())
    .then(data => {
        localSession = data.localSessionToken;
        updateChannels();
        updateMessages();
    });
}

function joinChannel() {
    let code = prompt("Enter channel share code");
}

function addFriend() {
    let code = prompt("Enter friend code");
}

function encodeStringToBytes(s) {
    // FIXME use utf-8 conversion instead
	var bytes = [];
	for (var i = 0; i < s.length; i++) {
		bytes[i] = s.charCodeAt(i);
	}
	return new Uint8Array(bytes);
}

async function readBlobAsync(blob) {
  return new Promise((resolve, reject) => {
    let reader = new FileReader();

    reader.onload = () => {
      resolve(reader.result);
    };

    reader.onerror = reject;

    reader.readAsText(blob);
  });
}

function send() {
    if (!localSession) {
        return;
    }
    let readSessionsDataUrl = baseUrl + "readSessionData?connection=" + connection + "&session=" + localSession;
    fetch(readSessionsDataUrl)
    .then(response => response.blob())
    .then(blob => readBlobAsync(blob))
    .then(blobText => {
        var oldMessages = []
        if (blobText) {
            try {
                let data = JSON.parse(blobText);
                oldMessages = data.messages;
            }
            catch(err) {
                console.log(err.message);
            }
        }
        // append form text as a message and write the data back
        let textField = document.getElementById("message");
        let newMessages = [{ 'sender' : displayName, 'message' : textField.value}];
        textField.value = "";

        let m = { 'messages' : oldMessages.concat(newMessages) };
        let s = JSON.stringify(m);
        let data = encodeStringToBytes(s);
        let octets = new Blob(data, {type: "application/octet-stream"});
        let octetsGETParam = encodeURIComponent(s);
        let writeSessionsDataUrl = baseUrl + "writeSessionData?connection=" + connection + "&session=" + localSession + "&data=" + octetsGETParam;
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

    let connectUrl = baseUrl + "connect.json?game=" + gameUUID;
    fetch(connectUrl)
    .then(response => response.json())
    .then(data => {
        connection = data.connectionToken;
        let loginUrl = baseUrl + "login.json?connection=" + connection + "&localDevice=" + deviceUUID;
        fetch(loginUrl)
        .then(response => response.json())
        .then(data => {
            localPlayer = data.localPlayerToken;
            createSessionUrl = baseUrl + "createSession.json?connection=" + connection + "&localPlayer=" + localPlayer;
            let displayNameUrl = baseUrl + "readPlayerDisplayName.json?connection=" + connection + "&localPlayer=" + localPlayer;
            fetch(displayNameUrl)
            .then(response => response.json())
            .then(data => {
                displayName = data.displayName;
                let p = document.getElementById("username");
                p.innerHTML = "Signed in as " + displayName;
            });
            let friendCodeUrl = baseUrl + "readPlayerFriendCode.json?connection=" + connection + "&localPlayer=" + localPlayer;
            fetch(friendCodeUrl)
            .then(response => response.json())
            .then(data => {
                let code = data.friendCode;
                let p = document.getElementById("friendcode");
                p.innerHTML = "Friend code : " + code;
            });
            updateChannels();
            updateFriends();
            updateMessages();
        });
    });
}
