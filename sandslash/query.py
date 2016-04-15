"""
    File containing classes and functions to handle a DNS Query
    @author Dosh, JRoc
"""
import struct, sqlite3
import answer
"""
    Class to represent a DNS query
    along with functions to decode it.
"""
class DNSQuery:
    def __init__(self):
        self.qID = None
        self.qCount = None
        self.ansCount = None
        self.authCount = None
        self.addCount = None
        self.names = []
        self.fullNames = []
        self.entries = []
        self.qCount = None
        self.qType = None
        self.checkin = False    # if a beacon is querying to check in

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

        # print out flags, move in function later
        """
        print "[QR %d] [OPC %d] [AA %d] [TC %d] [RD %d] [RA %d] [Z %d] [AD %d] [CD %d] [RCODE %d]" % \
               (qr, opcode, aa, tc, rd, ra, z, ad, cd, rcode)

        print "[# Questions: %d] [# Ans RR: %d] [# Auth RR: %d] [# Add RR: %d]" % \
                (self.qCount, self.ansCount, self.authCount, self.addCount)
        """

    """
        Decode the domain name sent in the query, unpack
        the first bit that tells the length of the name.
        Then continue to read each char until the terminating zero.

        query - the binary data received from the listening socket
        offset - the number of bits to offset by when unpacking the query

        returns - the new offset
    """
    def decode_name(self, query, offset):
        tmp = []    # tmp list to join names
        while True:
            #Get the length of the qName
            length, = struct.unpack_from("!B", query, offset)
            offset += 1
            if length == 0:
                break
            #Read the name from the data and store
            self.names += [struct.unpack_from("!%ds" % length, query, offset)]
            offset += length
        
        if self.names[0][0] == "check": self.checkin = True # beacon is checking in
        for x in self.names:
            tmp += [x[0]]   
        self.fullNames += ['.'.join(tmp)] # create the FQDN

        return offset

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
        i = 0
        #Read and decode each question
        for x in range(self.qCount):
            offset = self.decode_name(query, offset)
            self.qtype, qclass = qFormat.unpack_from(query, offset)
            offset += 4
            self.entries += [{"qName": self.fullNames[i], "qType": self.qtype, "qClass": qclass}]
            i+=1

        
"""
    Function to handle a DNS query, creating a class
    for it and calling the necessary functions.

    query - the binary data receieved from the listening socket
    addr - the address the data was received from
    server - class representing the mini dns server
"""
def handle_query(query, addr, server):

    q = DNSQuery()
    q.decode_question(query, 12)
    e = q.entries[0]
    
    found = False
    for x in server.beacons:                # check if its a beacon querying
        if x.ip == addr[0]:
            found = True
            if q.names[0][0] != "doshcloud" and q.names[0][0] != "check":
                x.output += [q.names[0][0]] # add the info the beacon sent back
            elif q.checkin:
                print "Beacon %d checking in" % (x.tag)
    
    if not found: 
        print ""
        print "Recieved query"
        print "[Q Name : %s] [Q Type : %s] [Q Class : %s]" % (e["qName"], e["qType"], e["qClass"])

    txt = True if int(q.qtype) == 16 else False
    answer.send_response(addr, server, q, txt)
