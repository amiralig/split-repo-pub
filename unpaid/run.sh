#!/bin/bash
export PATH=$PATH:/usr/local/bin
echo 'path is'+$PATH
whoami | xargs echo
echo 'Start running the unpaid report'
#if [ $1 ]; then 

echo "Going to download a new one"	
python /Users/amirali/PycharmProjects/CalendarICS/reports/__init__.py

#else
#	echo "Going to use the last downloaded one"
#fi

python /Users/amirali/PycharmProjects/CalendarICS/unpaid/__init__.py /Users/amirali/Documents/Life-VCC/lifeVCC-export-template-countifs.xlsx
