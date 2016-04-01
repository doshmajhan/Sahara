import socket
s = socket.socket()
port = 9998
s.bind(('', port))
f = open("recv.gg", 'wb')
s.listen(5)
while True:
    c, addr = s.accept()
    print "connect"
    l = c.recv(1)
    while l:
        f.write(l)
        l = c.recv(1)

    f.close()
    print "done"
    c.close()

