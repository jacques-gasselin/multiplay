class MPPlayer {
    constructor(displayName) {
        this.displayName = displayName;
    }
    getDisplayName() {
        return this.displayName;
    }
};

class MPPlayerFriend extends MPPlayer {
    constructor(connection, remotePlayerToken, displayName, alias) {
        super(displayName);
        this.connection = connection;
        this.remotePlayerToken = remotePlayerToken;
        this.alias = alias;
    }
    getAlias() {
        return this.alias;
    }
};

class MPSession {
    constructor(connection, sessionToken, displayName) {
        this.connection = connection;
        this.sessionToken = sessionToken;
        this.displayName = displayName;
    }
    getSessionToken() {
        return this.sessionToken;
    }
    getDisplayName() {
        return this.displayName;
    }
};

class MPLocalSession extends MPSession {
    constructor(connection, localSessionToken, displayName, shareCode) {
        super(connection, localSessionToken, displayName)
        this.shareCode = shareCode;
    }
    getShareCode() {
        return this.shareCode;
    }

    static async readBlobAsync(blob) {
        return new Promise((resolve, reject) => {
            let reader = new FileReader();
            reader.onload = () => {
                resolve(reader.result);
            };
            reader.onerror = reject;
            reader.readAsText(blob);
        });
    }

    fetchDataBlob() {
        let readSessionsDataUrl = this.connection.baseUrl + "readSessionData?connection=" + this.connection.connectionToken + "&session=" + this.sessionToken;
        return fetch(readSessionsDataUrl)
        .then(response => response.blob());
    }

    fetchDataAsJSON() {
        return this.fetchDataBlob()
        .then(blob => MPLocalSession.readBlobAsync(blob))
        .then(blobText => {
            if (blobText) {
                return JSON.parse(blobText);
            }
            return {};
        });
    }

    static encodeStringToBytes(s) {
        // FIXME use utf-8 conversion instead
        var bytes = [];
        for (var i = 0; i < s.length; i++) {
            bytes[i] = s.charCodeAt(i);
        }
        return new Uint8Array(bytes);
    }

    sendObjectAsJSONData(object) {
        let s = JSON.stringify(object);
        // Do this if POST
        //let data = encodeStringToBytes(s);
        //let octets = new Blob(data, {type: "application/octet-stream"});
        // Do this if GET
        let octetsGETParam = encodeURIComponent(s);
        let writeSessionsDataUrl = this.connection.baseUrl + "writeSessionData?connection=" + this.connection.connectionToken + "&session=" + this.sessionToken + "&data=" + octetsGETParam;
        return fetch(writeSessionsDataUrl);
    }
};

class MPLocalPlayer extends MPPlayer {
    constructor(connection, localPlayerToken, displayName, friendCode) {
        super(displayName);
        this.connection = connection;
        this.localPlayerToken = localPlayerToken;
        this.friendCode = friendCode;

        this.sessions = [];
        this.friends = [];
    }

    getLocalPlayerToken() {
        return this.localPlayerToken;
    }
    getFriendCode() {
        return this.friendCode;
    }

    getSessions() {
        return this.sessions;
    }

    addFriendWithCode(code) {
        let url = this.connection.baseUrl + "addPlayerFriend.json?connection=" + this.connection.connectionToken + "&localPlayer=" + this.localPlayerToken + "&friendCode=" + code
        return fetch(url)
        .then(response => response.json())
    }

    fetchSessions() {
        let listPlayerSessionsUrl = this.connection.baseUrl + "listPlayerSessions.json?connection=" + this.connection.connectionToken + "&localPlayer=" + this.localPlayerToken;
        return fetch(listPlayerSessionsUrl)
        .then(response => response.json())
        .then(data => {
            let sessions = data.sessions;
            var result = [];
            sessions.forEach(s => {
                result.push(new MPLocalSession(this.connection, s.localSessionToken, s.displayName, s.shareCode));
            });
            this.sessions = result;
            return result;
        });
    }

    fetchFriends() {
        let listPlayerFriendsUrl = this.connection.baseUrl + "listPlayerFriends.json?connection=" + this.connection.connectionToken + "&localPlayer=" + this.localPlayerToken;
        return fetch(listPlayerFriendsUrl)
        .then(response => response.json())
        .then(data => {
            let friends = data.friends;
            var result = [];
            friends.forEach(f => {
                result.push(new MPPlayerFriend(this.connection, f.remotePlayerToken, f.displayName, f.alias));
            });
            this.friends = result;
            return result;
        });
    }

    createSessionWithName(name) {
        let createSessionUrl = this.connection.baseUrl + "createSession.json?connection=" + this.connection.connectionToken + "&localPlayer=" + this.localPlayerToken;
        let url = createSessionUrl + '&displayName=' + encodeURIComponent(name)
        return fetch(url)
        .then(response => response.json())
        .then(data => {
            let session = new MPLocalSession(this.connection, data.localSessionToken, data.displayName, data.shareCode);
            this.sessions.push(session);
            return session;
        });
    }

    joinSessionByShareCode(shareCode) {
        let url = this.connection.baseUrl + "joinSession.json?connection=" + this.connection.connectionToken + "&localPlayer=" + this.localPlayerToken + "&sessionCode=" + shareCode;
        return fetch(url)
        .then(response => response.json())
        .then(data => {
            let session = this.sessions.find(s => s.sessionToken == data.localSessionToken);
            if (!session) {
                session = new MPLocalSession(this.connection, data.localSessionToken, data.displayName, data.shareCode);
                this.sessions.push(session);
            }
            return session;
        });
    }

    leaveSession(session) {
        let sessions = this.sessions;
        const index = sessions.indexOf(session);
        if (index > -1) {
            sessions.splice(index, 1);
        }
        this.sessions = sessions;
        let url = this.connection.baseUrl + "leaveSession.json?connection=" + this.connection.connectionToken + "&localPlayer=" + this.localPlayerToken + "&session=" + session.getSessionToken();
        return fetch(url)
        .then(response => response.json());
    }
};

class MPConnection {
    constructor(gameUUID, deviceUUID, baseUrl) {
        this.gameUUID = gameUUID;
        this.deviceUUID = deviceUUID;
        this.baseUrl = baseUrl;

        this.connectionToken = null;
        this.localPlayer = null;
    }

    /**
     * Connect to the game's instance of the multiplay service.
     * @return {Promise} a promise that is fulfilled when the game is connected.
     */
    connect() {
        let connectUrl = this.baseUrl + "connect.json?game=" + this.gameUUID;
        return fetch(connectUrl)
        .then(response => response.json())
        .then(data => {
            this.connectionToken = data.connectionToken;
        });
    }

    /**
     * Login the local player.
     * If the player has recently been logged in on this device this may return a
     * logged in an authorized player.
     * If the current device has no memory of the last time this player logged in,
     * or the server decides it can't trust the device an unathorized guest player
     * is returned.
     * You need to authorize the player to convert them from a guest into a previously
     * created authorized user.
     * @return {Promise} a promise that is fulfilled when player is logged in.
     */
    login() {
        let loginUrl = connection.baseUrl + "login.json?connection=" + this.connectionToken + "&localDevice=" + this.deviceUUID;
        return fetch(loginUrl)
        .then(response => response.json())
        .then(data => {
            let localPlayerToken = data.localPlayerToken;
            let displayName = data.displayName;
            let friendCode = data.friendCode;
            this.localPlayer = new MPLocalPlayer(this, localPlayerToken, displayName, friendCode);
        });
    }

    getLocalPlayer() {
        return this.localPlayer;
    }
};

/**
 * Concrete subclass of MPConnection to use when connection from a browser client with the 'window' context
 */
class MPBrowserConnection extends MPConnection {

    constructor(gameUUID) {
        var port = 12345;
        if (window.location.port) {
            port = window.location.port;
        }
        else if (window.location.protocol == 'http:') {
            port = 80;
        }
        else if (window.location.protocol == 'https:') {
            port = 443;
        }
        let baseUrl = window.location.protocol + '//' + window.location.hostname + ':' + port + '/';

        let deviceUUID = MPBrowserConnection.getCookie('multiplay-device'); // format is "00000000-0000-0000-0000-000000000000";
        if (!deviceUUID) {
            let a = MPBrowserConnection.randomHexString(4);
            let b = MPBrowserConnection.randomHexString(2);
            let c = MPBrowserConnection.randomHexString(2);
            let d = MPBrowserConnection.randomHexString(2);
            let e = MPBrowserConnection.randomHexString(6);
            deviceUUID = [a, b, c, d, e].join("-");
        }
        // keep it for 30 days by default
        MPBrowserConnection.setCookie('multiplay-device', deviceUUID, 30);

        super(gameUUID, deviceUUID, baseUrl);
    }

    static randomHexString(n) {
        let r = window.crypto.getRandomValues(new Uint8Array(n))
        let c = Array.prototype.map.call(r, b => b.toString(16).padStart(2, "0"));
        return c.join("");
    }

    static setCookie(cname, cvalue, exdays) {
      var d = new Date();
      d.setTime(d.getTime() + (exdays*24*60*60*1000));
      var expires = "expires="+ d.toUTCString();
      document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
    }

    static getCookie(cname) {
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
}