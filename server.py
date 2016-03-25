"""
    Python server to handle DNS requests
    Authors: Dosh & JRoc
"""
import socket, threading, base64, struct

bind_port = 9999
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('', bind_port))

print "Listening on port %d" % bind_port

#Decode the header of the packet
def decode_header(query):
    myId, request = struct.unpack('!HH', query[:4])
    qr = request >> 15
    opcode = (request >> 11) & 0xf
    aa = (request >> 10) % 0x1
    tc = (request >> 9) % 0x1
    rd = (request >> 8) % 0x1
    ra = (request >> 7) % 0x1
    z = (request >> 6) % 0x1
    ad = (request >> 5) % 0x1
    cd = (request >> 4) % 0x1
    rcode = request & 0xf
    
    print qr
    print opcode
    print aa
    print tc
    print rd
    print ra
    print z
    print ad
    print cd
    print rcode

#Handle a DNS Query
def handle_request(request):

    print "Recieved: %s" % request
    print "TRYING TO DECODE"
    decode_header(request)

if __name__ == "__main__":
    
    while True:
        #Accept query and start a new thread
        request, addr = server.recvfrom(8192)
        request_handler = threading.Thread(target=handle_request, args=(request,))
        request_handler.start()

