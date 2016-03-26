"""
    Python server to handle DNS requests
    Authors: Dosh & JRoc
"""
import socket, threading, base64, struct

bind_port = 9999
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('', bind_port))

print "Listening on port %d" % bind_port

class DNSQuery:
    def __init__(self):
        self.qID = None
        self.qCount = None
        self.ansCount = None
        self.authCount = None
        self.addCount = None
        self.names = []
        self.entries = []
        self.qCount = None
    
    #Decode the header of the packet
    def decode_header(self, query):
        #Read the data from the header, 12 bytes in total
        self.qID, flags, self.qCount, self.ansCount, \
        self.authCount, self.addCount  = struct.unpack('!HHHHHH', query[:12])
        qr = flags >> 15
        opcode = (flags >> 11) & 0xf
        aa = (flags >> 10) & 0x1
        tc = (flags >> 9) & 0x1
        rd = (flags >> 8) & 0x1
        ra = (flags >> 7) & 0x1
        z = (flags >> 6) & 0x1
        ad = (flags >> 5) & 0x1
        cd = (flags >> 4) & 0x1
        rcode = flags & 0xf
        
        print "[QR %d] [OPC %d] [AA %d] [TC %d] [RD %d] [RA %d] [Z %d] [AD %d] [CD %d] [RCODE %d]" % \
               (qr, opcode, aa, tc, rd, ra, z, ad, cd, rcode)

        print "[# Questions: %d] [# Ans RR: %d] [# Auth RR: %d] [# Add RR: %d]" % \
                (qCount, ansCount, authCount, addCount)

        return qCount

    #Decode the name of the server being queried
    def decode_name(self, query, offset):
        while True:
            #Get the length of the qName
            length, = struct.unpack_from("!B", query, offset)
            offset += 1
            if length == 0:
                return names, offset
            #Read the name from the data and store
            self.names += [struct.unpack_from("!%ds" % length, query, offset)]
            offset += length

    #Decode the variable length question body
    def decode_question(self, query, offset):
        qFormat = struct.Struct("!HH")
        self.qCount = decode_header(query)

        #Read and decode each question
        for x in range(qCount):
            qname, offset = decode_name(query, offset)
            qtype, qclass = qFormat.unpack_from(query, offset)
            offset += 4
            self.qEntries += [{"qName": qname, "qType": qtype, "qClass": qclass}]

class DNSResponse:
    def __init__(self, addr):
        self.addr = addr
        self.packet = None

    def create_packet(self):
        self.packet = struct.pack("!B", 12049)


#Handle a DNS Query
def handle_request(request, addr):
    
    query = DNSQuery()
    query.decode_question(request, 12)
    print query.entries

# Send response to query
def send_respone(addr):
    response = DNSResponse(addr)
    
if __name__ == "__main__":
    
    while True:
        #Accept query and start a new thread
        request, addr = server.recvfrom(8192)
        request_handler = threading.Thread(target=handle_request, args=(request, addr))
        request_handler.start()

