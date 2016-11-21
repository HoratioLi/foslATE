#!/bin/bash
# Script to set up posting unposted log scripts at regular intervals
echo "Setting up cron script"
echo "*/15 * * * * /home/pi/misfit/Production/src/scripts/postLogFiles.sh" > foo
crontab foo
crontab -l
rm foo
