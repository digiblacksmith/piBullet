#!/bin/bash -e
#(c) 2013 Aaron Land - Digital Blacksmith

SERVER_IP='10.9.8.250'

function install_first() {
	echo '(O) piBullet Virgin Installing... PHASE 1'
	sudo dpkg-reconfigure tzdata
	#sudo cp /usr/share/zoneinfo/US/Pacific /etc/localtime
	#sudo dpkg-reconfigure keyboard-configuration
	sed 's/XKBLAYOUT="gb"/XKBLAYOUT="us"/g' /etc/default/keyboard | sudo tee /etc/default/keyboard

	mkdir -p ~/piSaved
	rm -fr ~/Desktop ~/python_games
	rm -f ~/ocr_pi.png

	echo '(O) Upgrading...'
	sudo apt-get -qy update
	sudo apt-get -qy dist-upgrade

	echo '(O) Removing...'
	sudo apt-get -qy remove iptables smbclient wireless-tools wpasupplicant omxplayer
	#sudo apt-get -qy remove x11-common desktop-base gnome-accessibility-themes gnome-icon-theme fonts-droid
	sudo apt-get -qy autoremove --purge

	echo '(O) Installing favorites...'
	sudo apt-get -qy install imagemagick lftp tcpdump libav-tools
	sudo apt-get -qy autoremove

	echo '(O) Allowing broadcasts...'
	echo -n '#(O) piBullet
net.ipv4.icmp_echo_ignore_broadcasts = 0
' | sudo tee /etc/sysctl.d/42-piBullet.conf

	echo '(O) Setting up lftp...'
	echo '#(O) piBullet
set xfer:clobber on
' | sudo tee -a /etc/lftp.conf

	echo '(O) Setting up bash...'
	echo '#(O) piBullet
export PS1="\[\033[31m\]$PS1\[\033[0m\]"
' > ~/.bash_aliases

	echo "
alias cake.ping='ssh cake@$SERVER_IP'
alias cake.sftp='sftp cake@$SERVER_IP'
alias cake.ping='ping -c4 10.9.8.255'
alias pi.log='tail -f /home/pi/piBullet.log'
alias pi.app='sudo netstat --wide --symbolic --tcp --udp --listening --program --extend | grep 5001'
" >> ~/.bash_aliases

	echo '(O) Raspi Update'
	sudo rpi-update

	echo '[ dd if=/dev/diskX bs=1m | gzip > /image.iso.gz ]'
	echo '[ gzip -dc /image.iso.gz | dd of=/dev/diskX bs=1m ]'

	rm -f ~/.ssh/* ~/.bash_history
	echo -n '(O) Done! Shutting Down... [ RETURN ] '; read
	sudo shutdown -h now
}

function install_second() {
	echo '(O) piBullet Setup... PHASE 2'

	echo '(O) Setting hostname...'
	## This comes from the ip address
	HOSTN="pi`printf '%03d' $(ip addr show eth0 |  grep 'inet ' | awk '{print $2}' | cut -d. -f4 | cut -d/ -f1)`"
	echo $HOSTN | sudo tee /etc/hostname
	echo "127.0.1.1	$HOSTN" | sudo tee -a /etc/hosts

	echo '(O) Upgrading...'
	sudo apt-get -qy update
	sudo apt-get -qy upgrade
	sudo apt-get -qy autoremove --purge

	echo '(O) Setting up SSH...'
	mkdir -p ~/.ssh
	ssh-keygen -t rsa
	cat ~/.ssh/id_rsa.pub | ssh cake@$SERVER_IP 'cat >> .ssh/authorized_keys'
	ssh cake@$SERVER_IP 'cat .ssh/id_rsa.pub' > .ssh/authorized_keys

	echo '(O) Downloading piBullet.py...'
	lftp -u cake,cake -e "get piBullet.py; quit" $SERVER_IP
	chmod +x piBullet.py

	echo '(O) Setting startup...'
	echo '
# /\ Remove exit /\

#(O) piBullet
[ -r /home/pi/piBullet.py ] && /home/pi/piBullet.py

exit 0' | sudo tee -a /etc/rc.local
	sudo nano /etc/rc.local

	echo '(O) Expand && Turn on Camera! [return]'; read
	sudo raspi-config || true

	echo -n '(O) Done! Shutting Down... [ RETURN ] '; read
	sudo shutdown -h now
}

case $1 in
	1)		install_first;;
	2)		install_second;;
	*)		echo '1 = Virgin Raspbian Images Setup, 2 = Personalize Pi';;
esac
exit