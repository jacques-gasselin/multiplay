import http
import http.server

def run():
    server_address = ('', 12345)
    httpd = http.server.HTTPServer(server_address, http.server.BaseHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    run()
