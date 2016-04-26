"""
    Class and functions to represnt a beacon so
    the server can reference them easily

    Authors - Dosh, JRoc
"""

class Beacon:
    """
        Initializes a new beacon object
        
        ip = the ip address the beacon is located at
        tag = the id number of the beacon
        strtime - the string version of the time the beacon was created(hour, min, sec)
        realtime - the tuple of when the beacon was created(hour, min, sec)
    """
    def __init__(self, ip, tag, strtime, realtime):
        self.ip = ip
        self.tag = tag
        self.strtime = strtime    
        self.realtime = realtime    # the last time the beacon checked in
        self.cmds = []              # list of commands for this beacon to execute
        self.f = None               # file to send to this beacon
        self.output = 0
