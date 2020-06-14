'''
    Simple HTTP Server
    
    Copyright 2018 Jacques Gasselin
    
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
    
    http://www.apache.org/licenses/LICENSE-2.0
    
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

import http
import http.server
import uuid
import urllib.parse
import json
import sys
import os

class ServerInstance(object):
    def __init__(self, db):
        self.__db = db
        self.__db.open()

    def close(self):
        self.__db.close()

    def connect(self, handler, game):
        print("CONNECT game %s" % game)
        connectionUUID = self.__db.connect(handler.client_address[0], game)
        return { "connectionToken" : str(connectionUUID) }

    def login(self, handler, connection, localDevice):
        print("LOGIN connection %s on device %s " % (connection, localDevice))
        localPlayerUUID = self.__db.login(connection, localDevice)
        return { "localPlayerToken" : str(localPlayerUUID) }

    def writeplayerdata(self, handler, connection, localPlayer, data):
        print("WRITE PLAYER DATA '%s' FOR player %s ON connection %s " % (str(data), localPlayer, connection))
        success = self.__db.writePlayerData(connection, localPlayer, data)
        return { "status" : 1 if success else 0 }

    def readplayerdata(self, handler, connection, localPlayer):
        print("READ PLAYER DATA FOR player %s ON connection %s " % (localPlayer, connection))
        data = self.__db.readPlayerData(connection, localPlayer)
        return { "data" : str(data) }

    def writeplayerdisplayname(self, handler, connection, localPlayer, displayName):
        print("WRITE displayName '%s' FOR player %s ON connection %s " % (displayName, localPlayer, connection))
        success = self.__db.setPlayerDisplayName(connection, localPlayer, displayName)
        return { "status" : 1 if success else 0 }

    def readplayerdisplayname(self, handler, connection, localPlayer):
        print("READ displayName FOR player %s ON connection %s " % (localPlayer, connection))
        displayName = self.__db.getPlayerDisplayName(connection, localPlayer)
        return { "displayName" : str(displayName) }

    def readplayerfriendcode(self, handler, connection, localPlayer):
        print("READ friendCode for player %s ON connection %s " % (localPlayer, connection))
        friendCode = self.__db.getPlayerFriendCode(connection, localPlayer)
        return { "friendCode" : str(friendCode) }

    def listplayerfriends(self, handler, connection, localPlayer):
        print("LIST friends for player %s ON connection %s " % (localPlayer, connection))
        friendsAndNames = self.__db.listPlayerFriends(connection, localPlayer)
        friends = [{ 'remotePlayerToken' : str(s), 'displayName' : n} for s, n in friendsAndNames]
        return { "friends" : friends }

    def createsession(self, handler, connection, localPlayer, displayName=None):
        print("CREATE session '%s' FOR player %s ON connection %s " % (displayName if displayName else "<auto>", localPlayer, connection))
        localSessionUUID = self.__db.createSession(connection, localPlayer, displayName)
        return { "localSessionToken" : str(localSessionUUID) }

    def readsessiondisplayname(self, handler, connection, session):
        print("READ displayName FOR session %s ON connection %s " % (session, connection))
        displayName = self.__db.getSessionDisplayName(connection, session)
        return { "displayName" : str(displayName) }

    def writesessiondisplayname(self, handler, connection, session, displayName):
        print("WRITE displayName '%s' FOR session %s ON connection %s " % (displayName, session, connection))
        success = self.__db.setSessionDisplayName(connection, session, displayName)
        return { "status" : 1 if success else 0 }

    def listplayersessions(self, handler, connection, localPlayer):
        print("LIST sessions for player %s ON connection %s " % (localPlayer, connection))
        sessionsAndNames = self.__db.listPlayerSessions(connection, localPlayer)
        sessions = [{ 'localSessionToken' : str(s), 'displayName' : n} for s, n in sessionsAndNames]
        return { "sessions" : sessions }

    def chat(self, handler, message="", submit="", channel=""):
        return '''
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "https://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <header>
            <title>Multiplay Chat Client</title>
        </header>
        <body>
            <div id="user">
                <p id="username">Not logged in</p>
                <p id="friendcode">Not logged in</p>
            </div>
            <div>
                <div>
                    <p>Channels</p>
                    <button onclick="createChannel()">Create Channel</button>
                    <button onclick="joinChannel()">Join Channel</button>
                </div>
                <ul id="channels">
                </ul>
            </div>
            <div>
                <p>Friends</p>
                <button onclick="addFriend()">Add Friend</button>
                <ul id="friends">
                </ul>
            </div>
            <div id="messages">
            </div>
            <form id="chat-form">
                <input type="text" name="message">
                <input type="hidden" name="channel" id="channel">
                <input type="submit" name="submit" value="send">
            </form>
            <script type="text/javascript">
                let baseUrl = window.location.protocol + '//' + window.location.hostname + ':12345/';
                // global scope
                let gameUUID = "00000000-0000-0000-0000-000000000000";
                // FIXME, get the device UUID from a session token
                let deviceUUID = "00000000-0000-0000-0000-000000000000";
                let connection = "";
                let localPlayer = "";
                let localSession = "";
                
                let createSessionUrl = baseUrl + "createSession.json";
                
                function updateMessages() {
                    let readSessionsDataUrl = baseUrl + "readSessionData.json?connection=" + connection + "&session=" + localSession;
                    fetch(readSessionsDataUrl)
                    .then(response => response.json())
                    .then(data => {
                        let messages = data.messages;
                        let div = document.getElementById("messages");
                        result = '';
                        if (messages) {
                            messages.forEach(m => result = result + '<p>' + m.sender + ': ' + m.message + '</p>');
                        }
                        div.innerHTML = result;
                    });
                }
                
                function updateChannels() {
                    let listPlayerSessionsUrl = baseUrl + "listPlayerSessions.json?connection=" + connection + "&localPlayer=" + localPlayer;
                    fetch(listPlayerSessionsUrl)
                    .then(response => response.json())
                    .then(data => {
                        let channels = data.sessions;
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
                        session = data.localSessionToken;
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
                
                (function() {
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
                                let name = data.displayName;
                                let p = document.getElementById("username");
                                p.innerHTML = "Signed in as " + name;
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
                        });
                    });
                })();                
            </script>
        </body>
        </html>
        '''

    def favicon(self, handler):
        return ""

    def ico(self, handler):
        return ""

class PickleServerInstance(ServerInstance):
    def __init__(self):
        dbPath = ".simple_http_server.pickle"
        from backend import PickleBackend as Backend
        ServerInstance.__init__(self, Backend(dbPath))

class Sqlite3ServerInstance(ServerInstance):
    def __init__(self):
        dbPath = ".simple_http_server.db"
        from backend import Sqlite3Backend as Backend
        ServerInstance.__init__(self, Backend(dbPath))

class RequestHandler(http.server.BaseHTTPRequestHandler):
    serverInstance = None

    def _parse_GET(self):
        if '?' in self.path:
            command, argumentString = self.path.split("?")
        else:
            command = self.path
            argumentString = ""
        argumentValueByName = {}
        if len(argumentString) > 0:
            arguments = argumentString.split("&")
            for arg in arguments:
                try:
                    name, value = arg.split("=")
                except ValueError:
                    name = arg
                    value = ""
                argumentValueByName[name] = urllib.parse.unquote_plus(value)
        command, format = os.path.splitext(command)
        if format:
            argumentValueByName['response'] = format[1:]
        return command.lower(), argumentValueByName

    def _send_header(self, code, content_type):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def _GET_json(self, response):
        self._send_header(200, "application/json")
        self.wfile.write(("%s\n" % json.dumps(response)).encode())

    def _GET_ico(self, response):
        self._send_header(200, "image/x-icon")
        self.wfile.write(response.encode())

    def _GET_html(self, response):
        self._send_header(200, "text/html")
        self.wfile.write(response.encode())

    def _respond_error(self, code, error, format="json"):
        if format == "json":
            self._send_header(code, "application/json")
            self.wfile.write(('{ "error" : "%s" }\n' % str(error)).encode())
        else:
            self._send_header(code, "text/html")
            self.wfile.write(('error=%s\n' % str(error)).encode())

    def do_GET(self):
        print("GET")
        try:
            command, argumentValueByName = self._parse_GET()
        except ValueError as e:
            self._respond_error(400, e)
            return
        format = argumentValueByName.pop("response", "json")
        instance = RequestHandler.serverInstance
        try:
            func = getattr(instance, command[1:])
        except AttributeError as e:
            self._respond_error(400, e, format)
            return
        try:
            response = func(self, **argumentValueByName)
            print("-> ", response)
        except TypeError as e:
            self._respond_error(400, e, format)
            return
        except ValueError as e:
            self._respond_error(400, e, format)
            return
        if format == "html":
            self._GET_html(response)
        elif format == "ico":
            self._GET_ico(response)
        else:
            self._GET_json(response)

    def do_POST(self):
        print("POST")

__httpd = None

def run(port, useSSL = False):
    __serverInstanceClass = Sqlite3ServerInstance
    if 'pickle' in sys.argv:
        __serverInstanceClass = PickleServerInstance
    RequestHandler.serverInstance = __serverInstanceClass()

    server_address = ('', port)
    try:
        with http.server.HTTPServer(server_address, RequestHandler) as httpd:
            global __httpd
            if useSSL:
                import ssl
                #openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365
                httpd.socket = ssl.wrap_socket (httpd.socket,
                    keyfile=os.path.expanduser('~/.ssh/multiplay-server-key.pem'),
                    certfile=os.path.expanduser('~/.ssh/multiplay-server-cert.pem'),
                    server_side=True)
            __httpd = httpd
            print("serving at ", httpd.server_address)
            httpd.serve_forever()
    except:
        if RequestHandler.serverInstance:
            RequestHandler.serverInstance.close()

def runOnThread(port):
    import threading
    t = threading.Thread(target=run, args=(port,), daemon=True)
    t.start()
    import time
    time.sleep(0.1)

def shutdown():
    global __httpd
    httpd = __httpd
    if httpd:
        httpd.shutdown()
    if RequestHandler.serverInstance:
        RequestHandler.serverInstance.close()

if __name__ == "__main__":
    port = 12345
    useSSL = False
    for i, arg in enumerate(sys.argv):
        if arg == '-p' or arg == '--port':
            port = int(sys.argv[i + 1])
        if arg == '--https':
            useSSL = True
    run(port, useSSL)
