"""
    Python server to handle DNS requests
    Authors: Dosh & JRoc
"""
import socket, threading

bind_port = 53

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', bind_port))
server.listen(5)

print "Listening on %d" % bind_port

def handle_request(request_socket):
    
    request = request_socket.recv(2048)
    print "Recieved: %s" % request
    request_socket.send("ACK!")


if __name__ == "__main__":
    
    while True:
        request, addr = server.accept()
        request_handler = threading.Thread(target=handle_request, args=(request,))
        request_handler.start()

