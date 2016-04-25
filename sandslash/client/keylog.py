#! /usr/bin/python
# program to capture keystrokes
import struct

f = open("/dev/input/event2", 'rb')
fmat = 'llHHI'
size = struct.calcsize(fmat) # calculcate size of event struct

while True:
    e = f.read(size)
    (t_sec, t_usec, typeK, code, val) = struct.unpack(fmat, e) # seperate binary data
    if code !=0:
        print("Key: %u") % (code)
    else:
        print "--------------------------------"

f.close()
