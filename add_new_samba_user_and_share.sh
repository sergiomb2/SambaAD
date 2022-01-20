#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "please give a username. No arguments supplied."
    exit;
fi

useradd -m $1
passwd $1
usermod $1 -aG smbgrp
smbpasswd -a $1; # set smb password

# add user's private share
mkdir -p /srv/samba/$1;
chmod -R 0770 /srv/samba/$1;
chown -R root:smbgrp /srv/samba/$1;
chcon -t samba_share_t /srv/samba/$1;


echo "
 
[$1]
comment = Secure File Server Share of $1
path =  /srv/samba/$1
valid users = $1
guest ok = no
writable = yes
browsable = yes
" >> /etc/samba/smb.conf;

testparm; # test samba config

# restart service
systemctl restart smb.service;
systemctl restart nmb.service;

