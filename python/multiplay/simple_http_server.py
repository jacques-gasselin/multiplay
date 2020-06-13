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

    def writePlayerData(self, handler, connection, localPlayer, data):
        print("WRITE PLAYER DATA '%s' FOR player %s ON connection %s " % (str(data), localPlayer, connection))
        success = self.__db.writePlayerData(connection, localPlayer, data)
        return { "status" : 1 if success else 0 }

    def readPlayerData(self, handler, connection, localPlayer):
        print("READ PLAYER DATA FOR player %s ON connection %s " % (localPlayer, connection))
        data = self.__db.readPlayerData(connection, localPlayer)
        return { "data" : str(data) }

    def writePlayerDisplayName(self, handler, connection, localPlayer, displayName):
        print("WRITE displayName '%s' FOR player %s ON connection %s " % (displayName, localPlayer, connection))
        success = self.__db.setPlayerDisplayName(connection, localPlayer, displayName)
        return { "status" : 1 if success else 0 }

    def readPlayerDisplayName(self, handler, connection, localPlayer):
        print("READ displayName FOR player %s ON connection %s " % (localPlayer, connection))
        displayName = self.__db.getPlayerDisplayName(connection, localPlayer)
        return { "displayName" : str(displayName) }

    def readPlayerFriendCode(self, handler, connection, localPlayer):
        print("READ friendCode for player %s ON connection %s " % (localPlayer, connection))
        friendCode = self.__db.getPlayerFriendCode(connection, localPlayer)
        return { "friendCode" : str(friendCode) }

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
        command, argumentString = self.path.split("?")
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
            argumentValueByName['response'] = format
        return command, argumentValueByName

    def _send_header(self, code, content_type):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def _GET_json(self, response):
        self._send_header(200, "application/json")
        self.wfile.write(("%s\n" % json.dumps(response)).encode())

    def _GET_html(self, response):
        self._send_header(200, "text/html")
        lst = ['%s=%s' % (name, value) for name, value in response.items()]
        self.wfile.write(("%s\n"% "\n".join(lst)).encode())

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
        func = getattr(instance, command[1:])
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
        else:
            self._GET_json(response)

    def do_POST(self):
        print("POST")

__httpd = None

def run(port):
    __serverInstanceClass = PickleServerInstance
    if 'sqlite3' in sys.argv:
        __serverInstanceClass = Sqlite3ServerInstance
    RequestHandler.serverInstance = __serverInstanceClass()

    server_address = ('', port)
    try:
        with http.server.HTTPServer(server_address, RequestHandler) as httpd:
            global __httpd
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
    for i, arg in enumerate(sys.argv):
        if arg == '-p' or arg == '--port':
            port = int(sys.argv[i + 1])
    run(port)
