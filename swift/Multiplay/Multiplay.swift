
import Foundation
import SwiftyJSON

func fetch(url:URL?) -> JSON? {
    if url == nil {
        return nil
    }
    let semaphore = DispatchSemaphore(value: 0)
    var json: JSON?
    URLSession.shared.dataTask(with: url!) { data, res, err in
        if let data = data {
            json = try? JSON(data: data)
        }
        semaphore.signal()
    }.resume()
    _ = semaphore.wait(timeout: DispatchTime.now() + DispatchTimeInterval.milliseconds(500))
    return json
}

func encodeURIComponent(name: String!) -> String! {
    return name.addingPercentEncoding(withAllowedCharacters: NSMutableCharacterSet.urlQueryAllowed)
}

class MPPlayer {
    var displayName: String?

    init(withDisplayName name: String) {
        displayName = name;
    }
};

class MPPlayerFriend: MPPlayer {
    var connection: MPConnection?
    var remotePlayerToken: String?
    var alias: String?

    convenience init(withConnection c:MPConnection,
         remotePlayerToken r: String,
         displayName n: String,
         alias a: String) {
        self.init(withDisplayName:n)
        connection = c
        remotePlayerToken = r
        alias = a
    }
};

class MPSession {
    var connection: MPConnection?
    var sessionToken: String?
    var displayName: String?

    init(withConnection c:MPConnection,
         sessionToken t: String,
         displayName n: String) {
        connection = c
        sessionToken = t
        displayName = n
    }
};

class MPLocalSession: MPSession {
    var shareCode: String?
    
    convenience init(withConnection c:MPConnection,
         localSessionToken t: String,
         displayName n: String,
         shareCode sc: String) {
        self.init(withConnection: c, sessionToken: t, displayName: n)
        shareCode = sc
    }
}

class MPLocalPlayer: MPPlayer {
    var connection: MPConnection?
    var localPlayerToken: String?
    var friendCode: String?
    var authenticated: Bool = false
    var sessions: [MPLocalSession] = []
    var friends: [String] = []
    
    override var displayName: String? {
        get {
            return super.displayName
        }
        set(newName) {
            guard let connection = connection, connection.isConnected else { return }
            let comp = encodeURIComponent(name: newName!)
            if comp == nil {
                return
            }
            let url = connection.baseUrl! + "writeplayerdisplayname.json?connection=" + connection.connectionToken! + "&localPlayer=" + localPlayerToken! + "&displayName=" + comp!
            let result = fetch(url: URL(string: url))
            if result == nil {
                return
            }
            
            super.displayName = newName
        }
    }
    
    convenience init(withConnection c:MPConnection,
                     localPlayerToken r: String,
                     displayName n: String,
                     friendCode f: String,
                     authenticated a: Bool) {
        self.init(withDisplayName:n)
        connection = c
        localPlayerToken = r
        friendCode = f
        authenticated = a
    }

    func httpAuthenticate() -> Bool {
        guard let connection = connection, connection.isConnected else { return false }
        let url = connection.baseUrl! + "httpAuthenticate.json?connection=" + connection.connectionToken! + "&localPlayer=" + localPlayerToken!
        guard let json = fetch(url: URL(string: url))
        else {
            return false
        }
        if let s = json["localPlayerToken"].string {
            localPlayerToken = s
        }
        else {
            return false
        }
        if let s = json["displayName"].string {
            displayName = s
        }
        else {
            return false
        }
        if let s = json["friendCode"].string {
            friendCode = s
        }
        else {
            return false
        }
        if let s = json["authenticated"].bool {
            authenticated = s
        }
        else {
            return false
        }
        return false
    }

    func addFriendWithCode(code: String?) -> Bool {
        guard let connection = connection, connection.isConnected else { return false }
        guard let code = code else { return false }
        let url = connection.baseUrl! + "addPlayerFriend.json?connection=" + connection.connectionToken! + "&localPlayer=" + localPlayerToken! + "&friendCode=" + code
        let json = fetch(url: URL(string: url))
        return json != nil
    }

    func fetchSessions() -> [MPLocalSession] {
        guard let connection = connection, connection.isConnected else { return [] }
        let listPlayerSessionsUrl = connection.baseUrl! + "listPlayerSessions.json?connection=" + connection.connectionToken! + "&localPlayer=" + localPlayerToken!
        guard let json = fetch(url: URL(string: listPlayerSessionsUrl)) else { return [] }
        let sessions: Array<JSON>? = json["sessions"].array
        var result: [MPLocalSession] = []
        sessions?.forEach {
            if let lst = $0["localSessionToken"].string, let dn = $0["displayName"].string, let sc = $0["shareCode"].string {
                result.append(MPLocalSession(withConnection: connection, localSessionToken: lst, displayName: dn, shareCode: sc))
            }
        }
        return result
    }

    func fetchFriends() -> [MPPlayerFriend] {
        guard let connection = connection, connection.isConnected else { return [] }
        let listPlayerFriendsUrl = connection.baseUrl! + "listPlayerFriends.json?connection=" + connection.connectionToken! + "&localPlayer=" + localPlayerToken!
        guard let json = fetch(url: URL(string: listPlayerFriendsUrl)) else { return [] }
        let friends: Array<JSON>? = json["friends"].array
        var result: [MPPlayerFriend] = []
        friends?.forEach {
            if let rpt = $0["remotePlayerToken"].string, let dn = $0["displayName"].string, let a = $0["alias"].string {
                result.append(MPPlayerFriend(withConnection: connection, remotePlayerToken: rpt, displayName: dn, alias: a))
            }
        }
        return result
    }

    func createSessionWithName(name: String?) -> MPLocalSession? {
        guard let connection = connection, connection.isConnected else { return nil }
        guard let name = name else { return nil }
        if localPlayerToken == nil {
            return nil
        }
        var session: MPLocalSession? = nil
        sessions.forEach {
            if $0.displayName == name {
                session = $0
            }
        }
        if session != nil {
            return session
        }

        let createSessionUrl = connection.baseUrl! + "createSession.json?connection=" + connection.connectionToken! + "&localPlayer=" + localPlayerToken!
        let url = createSessionUrl + "&displayName=" + encodeURIComponent(name:name)
        if let json = fetch(url: URL(string: url)) {
            if let lst = json["localSessionToken"].string, let dn = json["displayName"].string, let sc = json["shareCode"].string {
                let session = MPLocalSession(withConnection: connection, localSessionToken: lst, displayName: dn, shareCode: sc)
                sessions.append(session)
                return session
            }
        }
        return nil
    }

    func joinSessionByShareCode(shareCode: String?) -> MPLocalSession? {
        guard let connection = connection, connection.isConnected else { return nil }
        guard let shareCode = shareCode else { return nil }
        guard let localPlayerToken = localPlayerToken else { return nil }
        let url = connection.baseUrl! + "joinSession.json?connection=" + connection.connectionToken! + "&localPlayer=" + localPlayerToken + "&sessionCode=" + shareCode
        guard let json = fetch(url: URL(string: url)) else { return nil }
        guard let sessionToken = json["localSessionToken"].string else { return nil }
        var session: MPLocalSession? = nil
        sessions.forEach {
            if $0.sessionToken == sessionToken {
                session = $0
            }
        }
        if session == nil {
            return nil
        }
        if let lst = json["localSessionToken"].string, let dn = json["displayName"].string, let sc = json["shareCode"].string {
            let session = MPLocalSession(withConnection: connection, localSessionToken: lst, displayName: dn, shareCode: sc)
            sessions.append(session)
            return session
        }
        return nil
   }

    func leaveSession(session: MPLocalSession?) {
        guard let connection = connection, connection.isConnected else { return }
        guard let session = session else { return }
        var existingSession: MPLocalSession? = nil
        sessions.forEach {
            if $0.sessionToken == session.sessionToken {
                existingSession = $0
            }
        }
        if existingSession == nil {
            return
        }

        let url = connection.baseUrl! + "leaveSession.json?connection=" + connection.connectionToken! + "&localPlayer=" + localPlayerToken! + "&session=" + session.sessionToken!
        if let _ = fetch(url: URL(string: url)) {
            /// @TODO iwhat validation is appropriate?
        }
    }
}

class MPConnection {
    var gameUUID: String?
    var deviceUUID: String?
    var baseUrl: String?
    var connectionToken: String?
    var localPlayer: MPLocalPlayer?
    var isConnected: Bool {
        get {
            return gameUUID != nil && deviceUUID != nil && baseUrl != nil && connectionToken != nil && localPlayer != nil
        }
    }
    
    init(withGameUUID g: String, deviceUUID d:String, baseUrl u:String) {
        gameUUID = g
        deviceUUID = d
        baseUrl = u
    }
    
    func connect() -> Bool {
        guard let baseUrl = baseUrl else { return false }
        guard let gameUUID = gameUUID else { return false }
        let connectUrl = baseUrl + "connect.json?game=" + gameUUID
        guard let json = fetch(url: URL(string: connectUrl)) else { return false }
        if let ct = json["connectionToken"].string {
            connectionToken = ct
            return true
        }
        return false
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
    func login() -> MPLocalPlayer? {
        if !self.isConnected { return nil }
        
        let loginUrl = baseUrl! + "login.json?connection=" + connectionToken! + "&localDevice=" + deviceUUID!
        if let json = fetch(url: URL(string: loginUrl)) {
            if let localPlayerToken = json["localPlayerToken"].string, let displayName = json["displayName"].string, let friendCode = json["friendCode"].string, let authenticated = json["authenticated"].bool {
                    let localPlayer = MPLocalPlayer(withConnection: self, localPlayerToken: localPlayerToken, displayName: displayName, friendCode: friendCode, authenticated: authenticated)
                self.localPlayer = localPlayer
                return localPlayer
            }
        }
        return nil
    }
}

/**
 * Concrete subclass of MPConnection to use when connection from a browser client with the 'window' context
 */

/*
class MPBrowserConnection: MPConnection {

    init(gameUUID: String?) {
        if gameUUID == nil {
            return
        }

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
*/
