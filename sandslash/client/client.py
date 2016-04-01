"""
    File containing classes and functions recieve responses from our custom DNS server
    @author Dosh, JRoc
"""
import struct, socket

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

    """
        Packs data into a binary struct to send as a
        response to the original query.

        url - the address of the answer
        qID - the queryID of the origina query
    """
    def create_query(self, url):
        self.packet = struct.pack("!H", 13567) # Q ID
        self.packet += struct.pack("!H", 640) # Flags
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
    Function to send DNS Query to custom server
"""
def send_query():
    addr="129.21.130.212"
    domain="doshcloud.com"
    print "Sending query"
    q = DNSQuery(addr)
    q.create_query(domain)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(bytes(q.packet), (addr, 53))
    print "Query sent"
    while True:
        s = sock.recv(2048)
        print s


if __name__ == '__main__':
    send_query()
