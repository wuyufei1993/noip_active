#!/bin/sh
#6*60*60 6小时
echo 'noip active run...'
sleep_time=21600
while :
  do
    echo `date '+%Y-%m-%d %H:%M:%S'` 'task run'
    python3 /opt/active_noip.py
    sleep $sleep_time
done