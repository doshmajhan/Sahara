"""
    Custom python server to handle DNS requests and 
    create custom responses to queries. Used primarily 
    to control DNS Beacons.

    @author Dosh, JRoc
    github.com/doshmajhan/Sandshrew
"""
import threading, sys
import server

"""
    Function to start interactive prompt to read commands

"""
def start_prompt():
    port = 53   # Default value
    cmd = ""

    while True:
        try:
            cmd = raw_input("[*] ")
        except (KeyboardInterrupt, SystemExit):
            print ""
            sys.exit()
              
        if cmd == "start":
            s = start_server(port)

        split_cmd = cmd.split(" ")
        if split_cmd[0] == "port":
            port = int(split_cmd[1])
         
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
