"""
    File containing classes and functions recieve responses from our custom DNS server
    @author Dosh, JRoc
"""
import struct, socket, sys

"""
    Class to represent a DNS Response and functions to build it
"""
class DNSQuery:
    """
        Init function to create the class
        
        addr - the address to send the packet too.
        txt - boolean value whether it's a txt record or not      
        server - the server sending the query
    """
    def __init__(self, addr):
        self.addr = addr
        self.packet = None
        self.qCount = None
        self.answer = None
        self.names = []
        self.data = ""
        self.frag = False       # if the incoming packet is fragmented
        self.isFile = False     # if the incoming packet is a file
    """
        Packs data into a binary struct to send as a
        response to the original query.

        url - the address of the answer
        qID - the queryID of the origina query
    """
    def create_query(self, url):
        self.packet = struct.pack("!H", 13567) # Q ID
        self.packet += struct.pack("!H", 302) # Flags
        self.packet += struct.pack("!H", 1) # Questions
        self.packet += struct.pack("!H", 0) # Answers
        self.packet += struct.pack("!H", 0) # Authorities
        self.packet += struct.pack("!H", 0) # Additional
        tmp_url = url.split(".")
        for x in tmp_url:
            self.packet += struct.pack("B", len(x)) # Store length of name
            self.packet += ''.join(struct.pack("c", byte) for byte in bytes(x)) # Loop & store name
        self.packet += struct.pack("B", 0) # Terminate name
        self.packet += struct.pack("!H", 16) # Q TXT Type
        self.packet += struct.pack("!H", 1) # Q Class
    
    """
        Decode the header of a DNS packet. First unpacks
        the data in certain sections at a time, then performs
        bitwise operations to get each field.

        query - the binary data received from the listening socket
    """
    def decode_header(self, query):
        #Read the data from the header, 12 bytes in total
        qID, flags, self.qCount, ansCount, \
        authCount, addCount  = struct.unpack('!HHHHHH', query[:12])
        qr = flags >> 15
        opcode = (flags >> 11) & 0xf
        aa = (flags >> 10) & 0x1
        tc = (flags >> 9) & 0x1
        rd = (flags >> 8) & 0x1
        ra = (flags >> 7) & 0x1
        z = (flags >> 6) & 0x1
        self.frag = True if int(z) == 1 else False       
        if int(z) == 1: self.isFile = True
        ad = (flags >> 5) & 0x1
        cd = (flags >> 4) & 0x1
        rcode = flags & 0xf
        
        
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
        names =[]
        while True:
            #Get the length of the qName
            length, = struct.unpack_from("!B", query, offset)
            offset += 1
            if length == 0:
                break
            #Read the name from the data and store
            names += [struct.unpack_from("!%ds" % length, query, offset)]
            offset += length
            
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
            qtype, qclass = qFormat.unpack_from(query, offset)
            offset += 4
            i+=1
        return offset
    
    """
        Decode the answer section of the DNS Query

        query - the binary data received from the listening socket
        offset - the number of bits to offset when unpacking the query
    """
    def decode_answer(self, query, offset):
        self.data = "" # Reset data 
        offset = self.decode_name(query, offset) # decode names in question 
        aType = struct.unpack_from("!H", query, offset) # decode answer record type
        offset+=2
        aClass = struct.unpack_from("!H", query, offset) # decode answer record class
        offset+=2
        ttl = struct.unpack_from("!I", query, offset) # decode answer record ttl
        offset+=4
        rdlength = struct.unpack_from("!H", query, offset) # decode answer record rd length
        offset+=2
        # make functional for all types of records later
        txtLen = struct.unpack_from("B", query, offset) # decode answer record txt length
        offset+=1
        for x in range(0, int(txtLen[0])): # loop and decode the data in the txt section
            self.data += struct.unpack_from("c", query, offset)[0]
            offset += 1
        

"""
    Function to send DNS Query to custom server
"""
def send_query():
    addr="129.21.130.212"
    domain="doshcloud.com"
    #print "Sending query"
    q = DNSQuery(addr)
    q.create_query(domain)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(bytes(q.packet), (addr, 53))
    #print "Query sent"
    fName = "output"
    f = open(fName, 'wb')
    # change to only write to file when file is specified
    while True:
        s = sock.recv(2048)
        q.answer = s
        offset = q.decode_question(q.answer, 12)
        q.decode_answer(q.answer, offset)
        if q.data != None:
            if q.data[:4] == "file":
                split_q = q.data.split()
                fName = split_q[1]
                f.close()
                f = open(fName, 'wb')
                q.frag = True
            elif q.isFile:
                # if data is a file, write to file
                # reconstruct to move into function
                for c in q.data:
                    f.write(c)

        if not q.frag: break
    
    if not q.isFile: 
        print q.data   # commands were sent
    else:
        print "file " + fName

    f.close()

if __name__ == '__main__':
    send_query()
