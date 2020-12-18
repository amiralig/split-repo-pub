#!/bin/bash
export PATH=$PATH:/usr/local/bin
echo 'path is'+$PATH
whoami | xargs echo
echo 'Start running the report gatherer r'
python /Users/amirali/PycharmProjects/CalendarICS/reports/__init__.py 6 12
python /Users/amirali/PycharmProjects/CalendarICS/sales/__init__.py /Users/amirali/Documents/Life-VCC/lifeVCC-export-template-countifs.xlsx /Users/amirali/Documents/Life-VCC/payroll
python /Users/amirali/PycharmProjects/CalendarICS/invoices/__init__.py /Users/amirali/Documents/Life-VCC/payroll 2019-02-01 2019-02-07