"""
    Custom python server to handle DNS requests and 
    create custom responses to queries. Used primarily 
    to control DNS Beacons.

    @author Dosh, JRoc
    github.com/doshmajhan/Sandshrew
"""
import server

# Main program to start the server and receive requests
if __name__ == "__main__":
        port = int(raw_input("Port: "))
        s = server.Server(port)
        s.start()
        exit(0)
