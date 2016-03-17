#!/bin/bash
# Takes script and deploys it to the beacons
# Author - Doshmajhan

# Reset file for new commands
sed -i '11,/-End/d' /etc/bind/dosh.cloud

# Loop through script and create TXT records for each command
x=1
while read LINE; do
    echo "$x       IN  TXT \"$LINE\"" >> /etc/bind/dosh.cloud
    let x=x+1
done
