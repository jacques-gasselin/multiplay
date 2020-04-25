import http
import http.server
import uuid
import urllib.parse
import json

class ServerInstance(object):
    def __init__(self):
        self.__gameByConnection = {}
        self.__localPlayerByConnection = {}
        self.__deviceByConnection = {}
        self.__playerByLocalPlayerAndConnection = {}
        self.__playerByDevice = {}
        self.__dataPerPlayerAndGame = {}

    def connect(self, handler, game):
        print("CONNECT game %s" % game)
        gameUUID = uuid.UUID(game)
        connectionUUID = uuid.uuid5(gameUUID, handler.client_address[0])
        self.__gameByConnection[connectionUUID] = gameUUID
        return { "connectionToken" : str(connectionUUID) }

    def login(self, handler, connection, localDevice):
        print("LOGIN connection %s on device %s " % (connection, localDevice))
        #print("__localPlayerByConnection = ", self.__localPlayerByConnection)
        localDeviceUUID = uuid.UUID(localDevice)
        connectionUUID = uuid.UUID(connection)
        self.__deviceByConnection[connectionUUID] = localDeviceUUID
        if connectionUUID in self.__localPlayerByConnection:
            print("  found local player for connection")
            localPlayerUUID = self.__localPlayerByConnection[connectionUUID]
            return { "localPlayerToken" : str(localPlayerUUID) }
        if localDeviceUUID in self.__playerByDevice:
            print("  player exists for device")
            playerUUID = self.__playerByDevice[localDeviceUUID]
        else:
            print("  create new player for device")
            playerUUID = uuid.uuid4()
            self.__playerByDevice[localDeviceUUID] = playerUUID
        localPlayerUUID = uuid.uuid5(localDeviceUUID, str(playerUUID))
        self.__localPlayerByConnection[connectionUUID] = localPlayerUUID
        self.__playerByLocalPlayerAndConnection[(localPlayerUUID, connectionUUID)] = playerUUID
        return { "localPlayerToken" : str(localPlayerUUID) }

    def writePlayerData(self, handler, connection, localPlayer, data):
        print("WRITE PLAYER DATA '%s' for player %s on connection %s " % (str(data), localPlayer, connection))
        connectionUUID = uuid.UUID(connection)
        localPlayerUUID = uuid.UUID(localPlayer)
        playerUUID = self.__playerByLocalPlayerAndConnection[(localPlayerUUID, connectionUUID)]
        gameUUID = self.__gameByConnection[connectionUUID]
        self.__dataPerPlayerAndGame[(playerUUID, gameUUID)] = data
        return { "status" : 1 }

    def readPlayerData(self, handler, connection, localPlayer):
        print("READ PLAYER DATA for player %s on connection %s " % (localPlayer, connection))
        connectionUUID = uuid.UUID(connection)
        localPlayerUUID = uuid.UUID(localPlayer)
        playerUUID = self.__playerByLocalPlayerAndConnection[(localPlayerUUID, connectionUUID)]
        gameUUID = self.__gameByConnection[connectionUUID]
        data = self.__dataPerPlayerAndGame[(playerUUID, gameUUID)]
        return { "data" : data }

import pickle
__serverInstance = None
def getServerInstance():
    global __serverInstance
    if not __serverInstance:
        try:
            with open(".simple_http_server_instance", "rb") as f:
                __serverInstance = pickle.load(f)
        except FileNotFoundError:
            pass
        if not __serverInstance:
            __serverInstance = ServerInstance()
    return __serverInstance

class RequestHandler(http.server.BaseHTTPRequestHandler):
    
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
        return command, argumentValueByName
    
    def _GET_json(self, response):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(("%s\n" % json.dumps(response)).encode())

    def _GET_html(self, response):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        lst = ['%s=%s' % (name, value) for name, value in response.items()]
        self.wfile.write(("%s\n"% "\n".join(lst)).encode())

    def _respond_error(self, code, error, format="json"):
        self.send_response(code)
        if format == "json":
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(('{ "error" : "%s" }\n' % str(error)).encode())
        else:
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(('error=%s\n' % str(error)).encode())

    def do_GET(self):
        print("GET")
        try:
            command, argumentValueByName = self._parse_GET()
        except ValueError as e:
            self._respond_error(400, e)
            return
        format = argumentValueByName.pop("response", "json")
        instance = getServerInstance()
        func = getattr(instance, command[1:])
        try:
            response = func(self, **argumentValueByName)
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

def run():
    server_address = ('', 12345)
    try:
        with http.server.HTTPServer(server_address, RequestHandler) as httpd:
            print("serving at ", httpd.server_address)
            httpd.serve_forever()
    except:
        if __serverInstance:
            with open(".simple_http_server_instance", "wb") as f:
                pickle.dump(__serverInstance, f)

if __name__ == "__main__":
    run()
