#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Jahratul Mim
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
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip().decode('utf-8')
        print(self.data)
        method, path = self.data.split("\r\n")[0].split(" ")


        # Handle non-GET requests
        if method != 'GET':
            response = b"HTTP/1.1 405 Method Not Allowed\r\n\r\nMethod Not Allowed"
            self.request.sendall(response)
            return
        
        # Construct absolute file path
        file_path = os.path.abspath(os.path.join('www', path[1:]))
        
        # Ensure the path is within ./www
        if not file_path.startswith(os.path.abspath('www')):
            response = b"HTTP/1.1 404 Not Found\r\n\r\nFile Not Found"
            self.request.sendall(response)
            return
        

        # Directory handling
        if os.path.isdir(file_path):
            if not path.endswith('/'):
                response = f"HTTP/1.1 301 Moved Permanently\r\nLocation: {path}/\r\n\r\n".encode('utf-8')
                self.request.sendall(response)
                return
            file_path = os.path.join(file_path, 'index.html')

        # File serving with MIME Types
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, 'rb') as file:
                content = file.read()
            # Set MIME type
            if file_path.endswith('.html'):
                mime_type = 'text/html'
                response = f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}\r\n\r\n".encode('utf-8') + content
            elif file_path.endswith('.css'):
                mime_type = 'text/css'
                response = f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}\r\n\r\n".encode('utf-8') + content
            else:
                response = b"HTTP/1.1 404 Not Found\r\n\r\nFile Not Found"

        else:
            # Return 404 if file not found
            response = b"HTTP/1.1 404 Not Found\r\n\r\nFile Not Found"
        
        # Send response
        self.request.sendall(response)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
