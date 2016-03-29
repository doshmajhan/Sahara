"""
    File containing classes and functions to handle a DNS Response
    @author Dosh, JRoc
"""
import struct

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
        self.packet += struct.pack("!H", 0) # Authorities
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
        self.packet += struct.pack("!H", 1) # Type 2 bytes
        self.packet += struct.pack("!H", 1) # Class 2 bytes
        self.packet += struct.pack("!I", 1) # TTL 4 bytes
        self.packet += struct.pack("!H", 4) # RDLENGTH 2 bytes
        self.packet += struct.pack("!I", 2165670612)  # RDATA, should be IP address from A record


"""
    Function to answer a DNS query with the correct record.

    addr - the address to send the response to
    server - the socket to send information to
    dnsQuery - the class represnting the query being answered
"""
def send_response(addr, server, dnsQuery):
    print "Sending response"
    response = DNSResponse(addr)
    response.create_packet("doshcloud.com", dnsQuery.qID)
    server.sendto(bytes(response.packet), addr)
    print "Response sent"
