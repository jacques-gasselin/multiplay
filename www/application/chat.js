let baseUrl = window.location.protocol + '//' + window.location.hostname + ':12345/';

// global scope
let gameUUID = "00000000-0000-0000-0000-000000000000";
// FIXME, get the device UUID from a session token
let connection = "";
let localPlayer = "";
let localSession = "";
let displayName = "";

let createSessionUrl = baseUrl + "createSession.json";

let queryString = window.location.search;
let urlParams = new URLSearchParams(queryString);
if (urlParams.has('channel')) {
    localSession = urlParams.get('channel');
}

function setCookie(cname, cvalue, exdays) {
  var d = new Date();
  d.setTime(d.getTime() + (exdays*24*60*60*1000));
  var expires = "expires="+ d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for(var i = 0; i <ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function randomHexString(n) {
    let r = window.crypto.getRandomValues(new Uint8Array(n))
    let c = Array.prototype.map.call(r, b => b.toString(16).padStart(2, "0"));
    return c.join("");
}

var deviceUUID = getCookie('multiplay-device'); //"00000000-0000-0000-0000-000000000000";
if (!deviceUUID) {
    let a = randomHexString(4);
    let b = randomHexString(2);
    let c = randomHexString(2);
    let d = randomHexString(2);
    let e = randomHexString(6);
    deviceUUID = [a, b, c, d, e].join("-");
    setCookie('multiplay-device', deviceUUID, 30);
}

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
        let chatUrl = baseUrl + "application/chat.html?channel=";
        channels.forEach(c => {
            result = result
             + '<li><a class="item" href="' + chatUrl + c.localSessionToken + '">' + c.shareCode + ': ' + c.displayName + '</a>'
             + '<button class="button-small" onclick="leaveChannel(\'' + c.localSessionToken +'\')">Leave</button>'
             + '</li>';
        });
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
    let url = baseUrl + "joinSession.json?connection=" + connection + "&localPlayer=" + localPlayer + "&sessionCode=" + code;
    fetch(url)
    .then(response => response.json())
    .then(data => {
        updateChannels();
    });
}

function leaveChannel(c) {
    let url = baseUrl + "leaveSession.json?connection=" + connection + "&localPlayer=" + localPlayer + "&session=" + c;
    fetch(url)
    .then(response => response.json())
    .then(data => {
        updateChannels();
    });
}

function addFriend() {
    let code = prompt("Enter friend code");
    let url = baseUrl + "addPlayerFriend.json?connection=" + connection + "&localPlayer=" + localPlayer + "&friendCode=" + code
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
