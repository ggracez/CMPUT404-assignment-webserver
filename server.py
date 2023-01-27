#  coding: utf-8 
import socketserver
import os

# Copyright 2023 Abram Hindle, Eddie Antonio Santos, Grace Zhu
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2023 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
       
    def handle(self):
        
        # status codes and messages
        STATUS_200 = "HTTP/1.1 200 OK\r\n"
        STATUS_301 = "HTTP/1.1 301 Moved Permanently\r\n"
        STATUS_404 = "HTTP/1.1 404 Not Found\r\n"
        STATUS_405 = "HTTP/1.1 405 Method Not Allowed\r\n"
        
        BASEDIR = "www"
        CODING = "utf-8"
        BASELOCATION = "http://127.0.0.1:8080/"
    
        
        self.data = self.request.recv(1024).strip()
        # print("Got a request of: %s\n" % self.data)
        
        method, req = self.data.decode().split("\r\n")[0].split()[0:2]
        req = req[1:]
        req_path = os.path.join(os.getcwd(), BASEDIR, os.path.normpath(req))
        # print("req_path:", req_path)
        
        # only GET is supported, all other methods return 405 error
        if method != "GET":
            self.request.sendall(bytearray(STATUS_405, CODING))
            return      
                
        # if directory (end with "/" or add it -> 301), default to index.html
        if os.path.isdir(req_path):
            if not req.endswith("/") and not len(req) == 0:
                headers = STATUS_301 + f"Location: {BASELOCATION}{req}/\r\n"
                self.request.sendall(bytearray(headers, CODING))
                return
            else:
                req_path = os.path.join(req_path, "index.html")
        
        # check if it is in the right directory
        temp_path = os.path.normpath(req_path)
        start_path = os.path.join(os.getcwd(), BASEDIR)
        if not temp_path.startswith(start_path):
            headers = STATUS_404 + "\r\n404 Not Found"
            self.request.sendall(bytearray(headers, CODING))
            return
        
        # check and read contents if it exists and return 200, else 404 error    
        if os.path.exists(req_path):
            f = open(req_path)
            content = "\r\n" + f.read()
            f.close()
            
            headers = STATUS_200
        
            if req_path.endswith(".css"):
                headers += "Content-Type: text/css\r\n"
            elif req_path.endswith(".html"):
                headers += "Content-Type: text/html\r\n"
            else:
                headers += "application/octet-stream\r\n"
        
            self.request.sendall(bytearray(headers + content, CODING))
        
        else:
            headers = STATUS_404 + "\r\n404 Not Found"
            self.request.sendall(bytearray(headers, CODING))
            

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()