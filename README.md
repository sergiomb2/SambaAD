# SambaAD
Samba AD packaging for Redhat 7 /Centos 7/ Fedora

- Based on https://negativo17.org/samba-4-active-directory-with-bind-dlz-zones-dynamic-dns-updates-windows-static-rpc-2/
- The first patch is for disabling MIT Kerberos integration and enabling optional Heimdal Kerberos with Domain Controller 
functionality in the Redhat/Fedora package i.e. with MIT Kerberos we not have a fully functional PDC.

