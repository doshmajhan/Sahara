"""
    Custom python server to handle DNS requests and 
    create custom responses to queries. Used primarily 
    to control DNS Beacons.

    Authors: Dosh & JRoc
    github.com/doshmajhan/Sandshrew
"""
import socket, threading, base64, struct

bind_port = 9999
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('', bind_port))

print "Listening on port %d" % bind_port

"""
    Class to represent a DNS Query and functions decode it
"""
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
    
    """
        Decode the header of a DNS packet. First unpacks 
        the data in certain sections at a time, then performs 
        bitwise operations to get each field.

        query - the binary data received from the listening socket
    """
    def decode_header(self, query):
        #Read the data from the header, 12 bytes in total
        self.qID, flags, self.qCount, self.ansCount, \
        self.authCount, self.addCount  = struct.unpack('!HHHHHH', query[:12])
        print flags
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
                (self.qCount, self.ansCount, self.authCount, self.addCount)

    """
        Decode the domain name sent in the query, unpack
        the first bit that tells the length of the name.
        Then continue to read each char until the terminating zero.

        query - the binary data received from the listening socket
        offset - the number of bits to offset by when unpacking the query

        returns - the new offset
    """
    def decode_name(self, query, offset):
        while True:
            #Get the length of the qName
            length, = struct.unpack_from("!B", query, offset)
            offset += 1
            if length == 0:
                return offset
            #Read the name from the data and store
            self.names += [struct.unpack_from("!%ds" % length, query, offset)]
            offset += length

    """
        Decode the question section of the DNS Query. 
        Loop for the number represented by qCount, and unpack
        the data, calling decode_name each time. Creates a new entry
        consisting of the name, type and class.

        query - the binary data received from the listening socket
        offset - the number of bits to offset by when unpacking the query
    """
    def decode_question(self, query, offset):
        qFormat = struct.Struct("!HH")
        self.decode_header(query)

        #Read and decode each question
        for x in range(self.qCount):
            offset = self.decode_name(query, offset)
            qtype, qclass = qFormat.unpack_from(query, offset)
            offset += 4
            self.entries += [{"qName": self.names, "qType": qtype, "qClass": qclass}]


"""
    Class to represent a DNS Response and functions to build it
"""
class DNSResponse:
    def __init__(self, addr):
        self.addr = addr
        self.packet = None

    """
        Packs data into a binary struct to send as a
        response to the original query. 

        url - the address of the answer
        qID - the queryID of the origina query
    """
    def create_packet(self, url, qID):
        self.packet = struct.pack("!H", qID) # Q ID
        self.packet += struct.pack("!H", 34176) # Flags
        self.packet += struct.pack("!H", 1) # Questions
        self.packet += struct.pack("!H", 1) # Answers
        self.packet += struct.pack("!H", 1) # Authorities
        self.packet += struct.pack("!H", 0) # Additional
        tmp_url = url.split(".")
        for x in tmp_url:
            self.packet += struct.pack("B", len(x)) # Store length of name
            for byte in bytes(x):
                self.packet += struct.pack("c", byte) # Store each char
        self.packet += struct.pack("B", 0) # Terminate name
        self.packet += struct.pack("!H", 1) # Q Type
        self.packet += struct.pack("!H", 1) # Q Class
        self.create_answer(url)

    """
        Creates the answer section of the DNS response

        record - the record to include in the name section
    """
    def create_answer(self, record):
        tmp_record = record.split(".")
        for x in tmp_record:
            self.packet += struct.pack("B", len(x)) # Store length of name
            for byte in bytes(x):
                self.packet += struct.pack("c", byte) # Store each char
        self.packet += struct.pack("B", 0) # Terminate name
        self.packet += struct.pack("!H", 1) # Type
        self.packet += struct.pack("!H", 1) # Class
        self.packet += struct.pack("B", 1) # TTL
        self.packet += struct.pack("B", 4) # RDLENGTH
        self.packet += struct.pack("L", 2165670612)  # RDATA, should be IP address from A record
        

"""
    Function to answer a DNS query with the correct record.

    addr - the address to send the response to
    server - the socket to send information to
    dnsQuery - the class represnting the query being answered
"""
def send_response(addr, server, dnsQuery):
    response = DNSResponse(addr)
    response.create_packet("dosh.cloud", dnsQuery.qID)
    server.sendto(bytes(response.packet), addr)

"""
    Function to handle a DNS query, creating a class
    for it and calling the necessary functions.

    query - the binary data receieved from the listening socket
    addr - the address the data was received from
    server - the socket to send information to
"""
def handle_query(query, addr, server):
    
    q = DNSQuery()
    q.decode_question(query, 12)
    print q.entries
    send_response(addr, server, q)


# Main program to start listening for queries
if __name__ == "__main__":
    
    while True:
        #Accept query and start a new thread
        query, addr = server.recvfrom(8192)
        query_handler = threading.Thread(target=handle_query, args=(query, addr, server))
        query_handler.start()

