#!/bin/bash
#(c) 2013 Aaron Land - Digital Blacksmith

echo 'cakeServer example Install script. Used with a clean copy of Ubuntu 12. NOT FOR GENERAL INSTALATION [ret]'
read

NET_CLASSC='10.9.8'
SERVER_ADDRESS="$NET_CLASSC.250"
DATA_HOME='/home/cake'

#-#
echo '(O) Upgrading...'
sudo apt-get -qy update
sudo apt-get -qy upgrade
sudo apt-get -qy autoremove

#-#
echo '(O) Installing favorites...'
sudo apt-get -qy install	openssh-server isc-dhcp-server ntp vsftpd \
							gpac libav-tools xubuntu-restricted-extras vlc

#-#
echo '(O) Setting up SSH...'
mkdir -p ~/.ssh
ssh-keygen -t rsa

#-#
echo '(O) Setting up Network...'

echo '# oSrvInstall
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.lo.disable_ipv6 = 1
net.ipv4.icmp_echo_ignore_broadcasts = 0
' | sudo tee /etc/sysctl.d/02-cake.ipv6disable.conf

echo '# oSrvInstall
blacklist ipv6
blacklist ip6_tables
' | sudo tee -a /etc/modprobe.d/blacklist-ipv6.conf

echo -n "# oSrvInstall
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet dhcp
	address $SERVER_ADDRESS
	netmask 255.255.255.0
" | sudo tee /etc/network/interfaces

#-#
echo '(O) Setting up DHCP...'
echo -n 'INTERFACES="eth0"' | sudo tee /etc/default/isc-dhcp-server
echo "## cake Server Install
ddns-update-style none;
default-lease-time 604800;
max-lease-time 604800;
authoritative;
option subnet-mask 255.255.255.0;
option routers $SERVER_ADDRESS
option ntp-servers $SERVER_ADDRESS;
option broadcast-address $NET_CLASSC.255;

subnet $NET_CLASSC.0 netmask 255.255.255.0 {
	range $NET_CLASSC.201 $NET_CLASSC.240;
}

host pi001 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.1; }
host pi002 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.2; }
host pi003 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.3; }
host pi004 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.4; }
host pi005 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.5; }
host pi006 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.6; }
host pi007 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.7; }
host pi008 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.8; }
host pi009 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.9; }
host pi010 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.10; }
host pi011 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.11; }
host pi012 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.12; }
host pi013 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.13; }
host pi014 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.14; }
host pi015 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.15; }
host pi016 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.16; }
host pi017 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.17; }
host pi018 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.18; }
host pi019 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.19; }
host pi020 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.20; }
host pi021 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.21; }
host pi022 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.22; }
host pi023 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.23; }
host pi024 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.24; }
host pi025 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.25; }
host pi026 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.26; }
host pi027 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.27; }
host pi028 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.28; }
host pi029 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.29; }
host pi030 { hardware ethernet b8:27:eb:aa:bb:cc; fixed-address $NET_CLASSC.30; }
" | sudo tee /etc/dhcp/dhcpd.conf

#-#
echo '(O) Setting up bash...'
echo '# oCamInstall
export PS1="\[\033[35m\]$PS1\[\033[0m\]"
' >> ~/.bash_aliases

echo "
alias cake.dhcp.leases='cat /var/lib/dhcp/dhcp.leases'
alias pi.pingall='ping -b -c2 $NET_CLASSC.255'

" >> ~./bash_aliases

#-#
echo '(O) Setting up system...'
mkdir -f $DATA_HOME/cakeSaved
mkdir -f $DATA_HOME/upload
sudo /usr/lib/lightdm/lightdm-set-defaults -l false
sudo sh -c "echo 'manual' > /etc/init/avahi-daemon.conf.override"
echo "
# /\ Remove exit /\

#(O) cakeServer
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A POSTROUTING -s $NET_CLASSC.0/24 -j MASQUERADE

exit" | sudo tee -a /etc/rc.local
sudo nano /etc/rc.local

#-#
echo '(O) Done!'
exit