import http
import http.server

class ServerIntance(object):
    def connect(self, game):
        print ("CONNECT game %s" % game)
        connectionToken = 0
        return { "connectionToken" : connectionToken }

    def login(self, connection, localDevice):
        print ("LOGIN connection %s on device %s " % (connection, localDevice))
        localPlayerToken = 0
        return { "localPlayerToken" : localPlayerToken }

class RequestHandler(http.server.BaseHTTPRequestHandler):
    
    def getServerInstance(self):
        try:
            return self.__serverInstance
        except AttributeError:
            self.__serverInstance = ServerIntance()
            return self.__serverInstance

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
                argumentValueByName[name] = value
        return command, argumentValueByName
    
    def _GET_json(self, response):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        
        lst = ['"%s" : "%s"' % (name, value) for name, value in response.items()]
        self.wfile.write(("{ %s } " % ", ".join(lst)).encode())

    def _GET_html(self, response):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        lst = ['%s=%s' % (name, value) for name, value in response.items()]
        self.wfile.write(("%s" % "\n".join(lst)).encode())

    def do_GET(self):
        print("GET")
        try:
            command, argumentValueByName = self._parse_GET()
        except ValueError as e:
            print(e)
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            return
        format = argumentValueByName.pop("response", "html")
        instance = self.getServerInstance()
        func = getattr(instance, command[1:])
        try:
            response = func(**argumentValueByName)
        except TypeError as e:
            self.send_response(400)
            if format == "json":
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(('{ "error" : "%s" }' % str(e)).encode())
            else:
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(('<html><body>\nerror=%s\n</body></html>' % str(e)).encode())
            return
        if format == "json":
            self._GET_json(response)
        else:
            self._GET_html(response)

    def do_POST(self):
        print("POST")

def run():
    server_address = ('', 12345)
    with http.server.HTTPServer(server_address, RequestHandler) as httpd:
        print("serving at ", httpd.server_address)
        httpd.serve_forever()

if __name__ == "__main__":
    run()
