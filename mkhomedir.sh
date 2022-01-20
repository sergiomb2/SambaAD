#!/bin/bash

HOMEDIR=/srv/samba/users
echo "$HOMEDIR/$1" > /tmp/users.txt
if [ ! -e $HOMEDIR/$1 ]; then
        mkdir $HOMEDIR/$1
        chown $1:"Domain Users" $HOMEDIR/$1
        chmod 700 $HOMEDIR/$1

fi
exit 0
