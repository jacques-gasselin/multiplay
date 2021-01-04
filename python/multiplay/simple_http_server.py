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

class HttpAuthException(Exception):
    pass

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
        localPlayer = self.__db.login(connection, localDevice)
        displayName = self.__db.getPlayerDisplayName(connection, localPlayer)
        friendCode = self.__db.getPlayerFriendCode(connection, localPlayer)
        authenticated = self.__db.isLocalPlayerAuthenticated(connection, localPlayer)
        return { "localPlayerToken" : str(localPlayer),
                 "displayName" : str(displayName),
                 "friendCode" : str(friendCode),
                 "authenticated" : 1 if authenticated else 0}

    def httpauthenticate(self, handler, connection, localPlayer):
        if not 'Authorization' in handler.headers:
            raise HttpAuthException()
        auth = handler.headers['Authorization']
        import base64
        auth_type, auth_bytes = auth.split(" ")
        username, password = base64.standard_b64decode(auth_bytes.encode()).decode().split(":")
        print("username:", username)
        print("password:", password)
        import hashlib
        md5 = hashlib.md5()
        md5.update(username.encode())
        md5.update(b':')
        md5.update(password.encode())
        if self.__db.authenticateLocalPlayer(connection, localPlayer, "HTTP " + auth_type, username, md5.hexdigest()):
            displayName = self.__db.getPlayerDisplayName(connection, localPlayer)
            friendCode = self.__db.getPlayerFriendCode(connection, localPlayer)
            authenticated = self.__db.isLocalPlayerAuthenticated(connection, localPlayer)
            return { "localPlayerToken" : str(localPlayer),
                     "displayName" : str(displayName),
                     "friendCode" : str(friendCode),
                     "authenticated" : 1 if authenticated else 0}
        return { "localPlayerToken" : "",
                 "displayName" : "",
                 "friendCode" : "",
                 "authenticated" : 0 }

    def writeplayerdata(self, handler, connection, localPlayer, data):
        print("WRITE PLAYER DATA '%s' FOR player %s ON connection %s " % (str(data), localPlayer, connection))
        success = self.__db.writePlayerData(connection, localPlayer, data)
        return "1".encode() if success else "0".encode()

    def readplayerdata(self, handler, connection, localPlayer):
        print("READ PLAYER DATA FOR player %s ON connection %s " % (localPlayer, connection))
        data = self.__db.readPlayerData(connection, localPlayer)
        return data

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

    def addplayerfriend(self, handler, connection, localPlayer, friendCode):
        print("ADD friend with friendCode %s to player %s ON connection %s " % (friendCode, localPlayer, connection))
        success = self.__db.addFriendToLocalPlayer(connection, localPlayer, friendCode)
        return { "status" : 1 if success else 0 }

    def listplayerfriends(self, handler, connection, localPlayer):
        print("LIST friends for player %s ON connection %s " % (localPlayer, connection))
        friendsAndNames = self.__db.listPlayerFriends(connection, localPlayer)
        friends = [{ 'remotePlayerToken' : str(s), 'displayName' : n} for s, n in friendsAndNames]
        return { "friends" : friends }

    def createsession(self, handler, connection, localPlayer, displayName=None):
        print("CREATE session '%s' FOR player %s ON connection %s " % (displayName if displayName else "<auto>", localPlayer, connection))
        localSessionUUID = self.__db.createSession(connection, localPlayer, displayName)
        displayName = self.__db.getSessionDisplayName(connection, localSessionUUID)
        shareCode = self.__db.getSessionShareCode(connection, localSessionUUID)
        return { "localSessionToken" : str(localSessionUUID), "displayName" : displayName, "shareCode" : shareCode  }

    def joinsession(self, handler, connection, localPlayer, sessionCode):
        print("JOIN session '%s' FOR player %s ON connection %s " % (sessionCode, localPlayer, connection))
        localSessionUUID = self.__db.joinSession(connection, localPlayer, sessionCode)
        displayName = self.__db.getSessionDisplayName(connection, localSessionUUID)
        shareCode = self.__db.getSessionShareCode(connection, localSessionUUID)
        return { "localSessionToken" : str(localSessionUUID), "displayName" : displayName, "shareCode" : shareCode  }

    def leavesession(self, handler, connection, localPlayer, session):
        print("LEAVE session '%s' FOR player %s ON connection %s " % (session, localPlayer, connection))
        success = self.__db.leaveSession(connection, localPlayer, session)
        return { "status" : 1 if success else 0 }

    def writesessiondata(self, handler, connection, session, data):
        print("WRITE SESSION DATA '%s' FOR session %s ON connection %s " % (str(data), session, connection))
        success = self.__db.writeSessionData(connection, session, data)
        return "1".encode() if success else "0".encode()

    def readsessiondata(self, handler, connection, session):
        print("READ SESSION DATA FOR session %s ON connection %s " % (session, connection))
        data = self.__db.readSessionData(connection, session)
        return data

    def readsessiondisplayname(self, handler, connection, session):
        print("READ displayName FOR session %s ON connection %s " % (session, connection))
        displayName = self.__db.getSessionDisplayName(connection, session)
        return { "displayName" : str(displayName) }

    def writesessiondisplayname(self, handler, connection, session, displayName):
        print("WRITE displayName '%s' FOR session %s ON connection %s " % (displayName, session, connection))
        success = self.__db.setSessionDisplayName(connection, session, displayName)
        return { "status" : 1 if success else 0 }

    def listsessionplayers(self, handler, connection, session):
        print("LIST players for session %s ON connection %s " % (session, connection))
        players = self.__db.listSessionPlayers(connection, session)
        return { "players" : players }

    def listplayersessions(self, handler, connection, localPlayer):
        print("LIST sessions for player %s ON connection %s " % (localPlayer, connection))
        sessionsNamesAndCodes = self.__db.listPlayerSessions(connection, localPlayer)
        sessions = [{ 'localSessionToken' : str(s), 'displayName' : n, 'shareCode' : c } for s, n, c in sessionsNamesAndCodes]
        return { "sessions" : sessions }

class PickleServerInstance(ServerInstance):
    def __init__(self):
        dbPath = os.path.expanduser("~/.multiplay-pickle.db")
        print("loading backend from ", dbPath)
        from backend import PickleBackend as Backend
        ServerInstance.__init__(self, Backend(dbPath))

class Sqlite3ServerInstance(ServerInstance):
    def __init__(self):
        dbPath = os.path.expanduser("~/.multiplay-sqlite3.db")
        print("loading backend from ", dbPath)
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

    def _write_content(self, content):
        if content:
            if len(content) >= 128: # Pick some value for which gzip is worth it
                if 'Accept-Encoding' in self.headers:
                    if 'gzip' in self.headers['Accept-Encoding']:
                        import gzip
                        content = gzip.compress(content)
                        self.send_header('Content-Encoding', 'gzip')
            self.send_header('Content-Length', str(len(content)))
            # CORS support
            self.send_header('Access-Control-Allow-Origin', "*")
            self.end_headers()
            self.wfile.write(content)
        else:
            self.end_headers()

    def _GET_json(self, response):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        content = ("%s\n" % json.dumps(response)).encode()
        self._write_content(content)

    def _GET_html(self, response):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self._write_content(response.encode())

    def _GET_binary(self, response):
        self.send_response(200)
        self.send_header("Content-type", "application/octet-stream")
        self._write_content(response)

    def _respond_error(self, code, error, format="json"):
        if format == "json":
            self.send_response(code)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(('{ "error" : "%s" }\n' % str(error)).encode())
        else:
            self.send_response(code)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(('error=%s\n' % str(error)).encode())

    def _GET_www_resource(self):
        rootPath = self.server.site_root_path
        if '?' in self.path:
            path, argumentString = self.path.split("?")
        else:
            path = self.path
            argumentString = ""
        # path has a prefix of / which would fail os.path.join
        filePath = os.path.join(rootPath, path[1:])
        try:
            with open(filePath, "rb") as f:
                data = f.read()
                self.send_response(200)
                if path.endswith(".html"):
                    self.send_header("Content-type", "text/html")
                elif path.endswith(".css"):
                    self.send_header("Content-type", "text/css")
                elif path.endswith(".js"):
                    self.send_header("Content-type", "application/javascript")
                elif path.endswith(".png"):
                    self.send_header("Content-type", "image/png")
                elif path.endswith(".ico"):
                    self.send_header("Content-type", "image/x-icon")
                self._write_content(data)
        except FileNotFoundError as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_GET(self):
        print("GET")
        try:
            command, argumentValueByName = self._parse_GET()
        except ValueError as e:
            self._respond_error(400, e)
            return
        format = argumentValueByName.pop("response", "binary")
        instance = RequestHandler.serverInstance
        try:
            func = getattr(instance, command[1:])
        except AttributeError as e:
            self._GET_www_resource()
            return
        try:
            response = func(self, **argumentValueByName)
            print("-> ", response)
        except HttpAuthException as e:
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="multiplay"')
            self.end_headers()
            self.wfile.write(str("0").encode())
            return
        except TypeError as e:
            self._respond_error(400, e, format)
            return
        except ValueError as e:
            self._respond_error(400, e, format)
            return
        try:
            if format == "html":
                self._GET_html(response)
            elif format == "ico":
                self._GET_ico(response)
            elif format == "json":
                self._GET_json(response)
            else:
                self._GET_binary(response)
        except TypeError as e:
            print(e)
            self._respond_error(400, e, format)


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
        with http.server.ThreadingHTTPServer(server_address, RequestHandler) as httpd:
            global __httpd
            if useSSL:
                import ssl
                #openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365
                httpd.socket = ssl.wrap_socket (httpd.socket,
                    keyfile=os.path.expanduser('~/.ssh/multiplay-server-key.pem'),
                    certfile=os.path.expanduser('~/.ssh/multiplay-server-cert.pem'),
                    server_side=True)
                print("serving at https://", httpd.server_address)
            else:
                print("serving at http://localhost:%i" % port)
                print("chat client at http://localhost:%i/application/chat.html" % port)
            __httpd = httpd
            currentFilePath = os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
            httpd.site_root_path = os.path.realpath(os.path.join(currentFilePath, '..', '..', '..', 'www'))
            print("loading resources from ", httpd.site_root_path)
            httpd.serve_forever()
    except KeyboardInterrupt: # silly special cases that don't derive from Exception for common Unix ways to kill threads
        pass
    except Exception as e:
        print(e)
    finally:
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
