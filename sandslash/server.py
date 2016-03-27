"""
    File containing classes and functions to create
    the DNS server and handle queries/repsonses
    @author Dosh, JRoc
"""
import socket, threading
import query

"""
    Class to represent the base of the DNS server

    port - the port number to bind to
"""
class Server:
    def __int__(self, port):
        self.port= port
        self.sock = None

    """
        Function to start the server with the information
        in the server

    """
    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.port))

        print "Listening on port %d" % self.port

        while True:
            #Accept query and start a new thread
            q, addr = self.sock.recvfrom(8192)
            query_handler = threading.Thread(target=query.handle_query, args=(q, addr, self.sock))
            query_handler.start()
