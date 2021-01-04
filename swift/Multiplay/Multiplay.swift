
import Foundation
import SwiftyJSON

func fetch(url:URL?) -> JSON? {
    guard let url = url else { return nil }
    let semaphore = DispatchSemaphore(value: 0)
    var json: JSON?
    var timedOut = true
    URLSession.shared.dataTask(with: url) { data, res, err in
        if let data = data {
            json = try? JSON(data: data)
            print("Read ", data.count, " bytes\n")
        }
        else {
            print("Failed to read url: ", url.absoluteString)
        }
        timedOut = false
        semaphore.signal()
    }.resume()
    _ = semaphore.wait(timeout: DispatchTime.now() + DispatchTimeInterval.milliseconds(500))

    if timedOut {
        print("Request timed out for: ", url.absoluteString)
    }
    return json
}

func authenticate(url:URL?) -> JSON? {
    guard let url = url else { return nil }
    let request = URLRequest(url:url)
    let config = URLSessionConfiguration.default
    let userPassword = "StarLord89:69"
    let passwordData = userPassword.data(using: String.Encoding.utf8)
    guard let base64EncodedCredential = passwordData?.base64EncodedString(options: Data.Base64EncodingOptions(rawValue: 0)) else { return nil }
    let authString = "Basic \(base64EncodedCredential)"
    config.httpAdditionalHeaders = ["Authorization" : authString]

    let semaphore = DispatchSemaphore(value: 0)
    var timedOut = true
    var json: JSON?
    let task = URLSession.shared.dataTask(with: request) { (data, response, error) -> Void in
        if let data = data {
            json = try? JSON(data: data)
            print("Read ", data.count, " bytes\n")
        }
        else {
            print("Failed to read url: ", url.absoluteString)
        }
        timedOut = false
        semaphore.signal()
    }

    _ = semaphore.wait(timeout: DispatchTime.now() + DispatchTimeInterval.milliseconds(500))
    task.resume()

    if timedOut {
        NSLog("Authentication timed out for")
    }
    
    return json
}

func encodeURIComponent(name: String!) -> String! {
    return name.addingPercentEncoding(withAllowedCharacters: NSMutableCharacterSet.urlQueryAllowed)
}

class Player {
    var displayName: String?

    init(withDisplayName name: String) {
        displayName = name;
    }
}

class FriendPlayer: Player {
    var connection: Connection?
    var remotePlayerToken: String?
    var alias: String?

    convenience init(withConnection c:Connection,
         remotePlayerToken r: String,
         displayName n: String,
         alias a: String) {
        self.init(withDisplayName:n)
        connection = c
        remotePlayerToken = r
        alias = a
    }
}

class SessionBase : Hashable {
    static func == (lhs: SessionBase, rhs: SessionBase) -> Bool {
        return lhs.connection == rhs.connection && lhs.sessionToken == rhs.sessionToken && lhs.displayName == rhs.displayName
    }
    
    func hash(into hasher: inout Hasher) {
        hasher.combine(sessionToken)
        hasher.combine(displayName)
    }

    var connection: Connection?
    var sessionToken: String?
    var displayName: String?

    init(withConnection c:Connection,
         sessionToken t: String,
         displayName n: String) {
        connection = c
        sessionToken = t
        displayName = n
    }
    
    var players: [String] {
        get {
            guard let connection = connection else { return [] }
            guard let baseUrl = connection.baseUrl else { return [] }
            guard let jsonx : JSON = fetchDataAsJson(url: URL(string: baseUrl)) else { return [] }
            print("Read json ", jsonx.count)
            var result: [String] = []
            return result
        }
    }
    
    func fetchDataAsJson(url:URL?) -> JSON? {
        guard let connection = connection else { return nil }
        guard let url = url else { return nil }
        let path = url.absoluteString
        guard let ct = connection.connectionToken else { return nil }
        guard let st = sessionToken else { return nil }
        let dataPath = path + "listSessionPlayers.json?connection=" + ct + "&session=" + st
        let result = fetch(url: URL(string:dataPath))
        NSLog("fetching %@ %@", dataPath, result == nil ? "failed" : "succeeded")
        return result
    }
}

class Session: SessionBase {
    var shareCode: String?
    
    convenience init(withConnection c:Connection,
         localSessionToken t: String,
         displayName n: String,
         shareCode sc: String) {
        self.init(withConnection: c, sessionToken: t, displayName: n)
        shareCode = sc
    }
}

class LocalPlayer: Player, Hashable {
    static func == (lhs: LocalPlayer, rhs: LocalPlayer) -> Bool {
        guard let lct = lhs.connection else { return false }
        guard let rct = rhs.connection else { return false }
        return lct.connectionToken == rct.connectionToken && lhs.localPlayerToken == rhs.localPlayerToken && lhs.friendCode == rhs.friendCode
    }

    func hash(into hasher: inout Hasher) {
        hasher.combine(localPlayerToken)
        hasher.combine(friendCode)
    }
    
    var connection: Connection?
    var localPlayerToken: String?
    var friendCode: String?
    var authenticated: Bool = false
    var sessions: [Session] = []
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
    
    convenience init(withConnection c:Connection,
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

    func authenticate() -> Bool {
        guard let connection = connection, connection.isConnected else { return false }
        let url = connection.baseUrl! + "httpAuthenticate.json?connection=" + connection.connectionToken! + "&localPlayer=" + localPlayerToken!
        guard let json = Multiplay.authenticate(url: URL(string: url))
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

    func fetchSessions() -> [Session] {
        guard let connection = connection, connection.isConnected else { return [] }
        let listPlayerSessionsUrl = connection.baseUrl! + "listPlayerSessions.json?connection=" + connection.connectionToken! + "&localPlayer=" + localPlayerToken!
        guard let json = fetch(url: URL(string: listPlayerSessionsUrl)) else { return [] }
        let sessions: Array<JSON>? = json["sessions"].array
        var result: [Session] = []
        sessions?.forEach {
            if let lst = $0["localSessionToken"].string, let dn = $0["displayName"].string, let sc = $0["shareCode"].string {
                result.append(Session(withConnection: connection, localSessionToken: lst, displayName: dn, shareCode: sc))
            }
        }
        return result
    }

    func fetchFriends() -> [FriendPlayer] {
        guard let connection = connection, connection.isConnected else { return [] }
        let listPlayerFriendsUrl = connection.baseUrl! + "listPlayerFriends.json?connection=" + connection.connectionToken! + "&localPlayer=" + localPlayerToken!
        guard let json = fetch(url: URL(string: listPlayerFriendsUrl)) else { return [] }
        let friends: Array<JSON>? = json["friends"].array
        var result: [FriendPlayer] = []
        friends?.forEach {
            if let rpt = $0["remotePlayerToken"].string, let dn = $0["displayName"].string, let a = $0["alias"].string {
                result.append(FriendPlayer(withConnection: connection, remotePlayerToken: rpt, displayName: dn, alias: a))
            }
        }
        return result
    }

    func createSession(name: String?) -> Session? {
        guard let connection = connection, connection.isConnected else { return nil }
        guard let name = name else { return nil }
        if localPlayerToken == nil {
            return nil
        }
        var session: Session? = nil
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
                let session = Session(withConnection: connection, localSessionToken: lst, displayName: dn, shareCode: sc)
                sessions.append(session)
                return session
            }
        }
        return nil
    }

    func joinSessionByShareCode(shareCode: String?) -> Session? {
        guard let connection = connection, connection.isConnected else { return nil }
        guard let shareCode = shareCode else { return nil }
        guard let localPlayerToken = localPlayerToken else { return nil }
        let url = connection.baseUrl! + "joinSession.json?connection=" + connection.connectionToken! + "&localPlayer=" + localPlayerToken + "&sessionCode=" + shareCode
        guard let json = fetch(url: URL(string: url)) else { return nil }
        guard let sessionToken = json["localSessionToken"].string else { return nil }
        var session: Session? = nil
        sessions.forEach {
            if $0.sessionToken == sessionToken {
                session = $0
            }
        }
        if session != nil {
            return nil
        }
        if let lst = json["localSessionToken"].string, let dn = json["displayName"].string, let sc = json["shareCode"].string {
            let session = Session(withConnection: connection, localSessionToken: lst, displayName: dn, shareCode: sc)
            sessions.append(session)
            return session
        }
        return nil
   }

    func leaveSession(session: Session?) {
        guard let connection = connection, connection.isConnected else { return }
        guard let session = session else { return }
        var existingSession: Session? = nil
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

class Connection : Hashable {
    static func == (lhs: Connection, rhs: Connection) -> Bool {
        guard let lp = lhs.localPlayer else { return false }
        guard let rp = rhs.localPlayer else { return false }
        return lhs.gameUUID == rhs.gameUUID && lhs.deviceUUID == rhs.deviceUUID && lhs.baseUrl == rhs.baseUrl && lhs.connectionToken == rhs.connectionToken && lp.localPlayerToken == rp.localPlayerToken
    }
    
    func hash(into hasher: inout Hasher) {
        hasher.combine(gameUUID)
        hasher.combine(deviceUUID)
        hasher.combine(baseUrl)
        hasher.combine(connectionToken)
    }

    var gameUUID: String?
    var deviceUUID: String?
    var baseUrl: String?
    var connectionToken: String?
    var localPlayer: LocalPlayer?
    var isConnected: Bool {
        get {
            return gameUUID != nil && deviceUUID != nil && baseUrl != nil && connectionToken != nil
        }
    }
    var isLoggedIn: Bool {
        get {
            return isConnected && localPlayer != nil
        }
    }
    
    init(gameUUID g: String, deviceUUID d:String, baseUrl u:String) {
        gameUUID = g
        baseUrl = u.last! == "/" ? u : u + "/"
        deviceUUID = d
    }

    init(gameUUID g: String, baseUrl u:String) {
        gameUUID = g
        baseUrl = u.last! == "/" ? u : u + "/"
        deviceUUID = UUID().uuidString
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
    func login() -> LocalPlayer? {
        if !self.isConnected { return nil }
        
        let loginUrl = baseUrl! + "login.json?connection=" + connectionToken! + "&localDevice=" + deviceUUID!
        if let json = Multiplay.fetch(url: URL(string: loginUrl)) {
            if let localPlayerToken = json["localPlayerToken"].string, let displayName = json["displayName"].string, let friendCode = json["friendCode"].string, let authenticated = json["authenticated"].int {
                let localPlayer = LocalPlayer(withConnection: self, localPlayerToken: localPlayerToken, displayName: displayName, friendCode: friendCode, authenticated: authenticated != 0 ? true : false)
                self.localPlayer = localPlayer
                return localPlayer
            }
        }
        return nil
    }
}

