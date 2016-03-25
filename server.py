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
    queryId, flags, qCount, ansCount, authCount, addCount  = struct.unpack('!HHHHHH', query[:12])
    qr = flags >> 15
    opcode = (flags >> 11) & 0xf
    aa = (flags >> 10) % 0x1
    tc = (flags >> 9) % 0x1
    rd = (flags >> 8) % 0x1
    ra = (flags >> 7) % 0x1
    z = (flags >> 6) % 0x1
    ad = (flags >> 5) % 0x1
    cd = (flags >> 4) % 0x1
    rcode = flags & 0xf
    
    print "[QR %d] [OPC %d] [AA %d] [TC %d] [RD %d] [RA %d] [Z %d] [AD %d] [CD %d] [RCODE %d]" % \
           (qr, opcode, aa, tc, rd, ra, z, ad, cd, rcode)

    print "[# Questions: %d] [# Ans RR: %d] [# Auth RR: %d] [# Add RR: %d]" % \
            (qCount, ansCount, authCount, addCount)

    return qCount

#Decode the variable length question body
def decode_question (query, offset):
    qFormat = struct.Struct("!HH")
    qEntries = []
    qCount = decode_header(query
    while x < qCount:
        qtype, qclass = qFormat.unpack_from(query_body, offset)
        offset += 2
        qEntries += [{"qType": qtype, "qClass": qclass}]
        x+=1

    return qEntries  
    
#Handle a DNS Query
def handle_request(request):

    print "Recieved: %s" % request
    print "TRYING TO DECODE"
    entries = decode_question(request, 12)
    print entries

if __name__ == "__main__":
    
    while True:
        #Accept query and start a new thread
        request, addr = server.recvfrom(8192)
        request_handler = threading.Thread(target=handle_request, args=(request,))
        request_handler.start()

