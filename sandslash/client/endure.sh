#! /bin/bash
#   Doshmajahn
#   Script that looks for if the beacon is running
#   if not it restarts it

search(){
    string="/bin/bash ./digg.sh"
    output=$(ps aux | grep digg.sh)
    if [[ $output == *$string* ]]; then
        echo "found it"
    else
        echo "not running"
        echo "starting back up"
        /bin/bash digg.sh
        echo "started"
    fi
}


main(){
    while true; do
        sleep 10
        search
    done
}

main
