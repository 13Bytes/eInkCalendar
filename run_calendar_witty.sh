#!/bin/bash

#Will run the script for refreshing the screen and then shutdown the system.
cd $(dirname $0)

./run_calendar.sh

# Check if the startup was due to a schedule in witty pi
#Get the reason of the startup
result=$(/usr/sbin/i2cget -y 1 0x08 11)
#If is 1 is was due to ALARM1 that is the alarm for the scheduled startup 
if [[ "$result" == "0x01" ]]; then
	echo "Startup due to schelude in witty pi. Will shutdown in 20s"
	for i in {20..1}
	do
    	echo "$i"
    	sleep 1
    done
    # If the result is 1, run the shutdown command
    /usr/bin/sudo shutdown -h +1
else
    echo "No scheduled startup detected. The system will not be shutting down."
fi
