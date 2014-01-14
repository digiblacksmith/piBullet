piBullet
#(c) 2013 Aaron Land - Digital Blacksmith
========

Raspberry Pi bullet-time server and camera python code

I built this for the Optimist LA (www.optimistla.com) Christmas party. The program ran a random selection 
of sequences and generated a 1MB file that was emailed to someone on the spot. It uses 30 Raspberries in a
1/4 circle with about a 20 foot radius. This is my very first Python program! Many of the items are
hardcoded, but it is designed to run on a private network and was built as a prototype.

After much testing with the camera module I found the following project to work the best:
https://bitbucket.org/niklas_rother/rasperry-pi-userland/raw/master/host_applications/linux/apps/raspicam/raspifastcamd_scripts
It removees the delay of turning on and off the camera, is high quality, and can reach 3.44fps. 
Suprisingly raspistill only achieved 1.45fps. I could achieve 9.45fps with picamera but the image 
qulaity was unuseable. MY TEST SCRIPTS ARE INCLUDED

== SETUP ==

INSTALLER SCRIPTS ONLY TO BE USED IN DEDICATED VIRGIN ENVIRONMENTS! NOT FOR GENERAL USE!!

PIs
- 30 Model Bs with case and camera module (Any number will do)
- Connected via Fast Ethernet to a central Server and set to DHCP
 + In my setup every 10 had a switch, each were connected to a centreal switch which also connected
   to the server to ensure similar latency.
- 4-5 Pi's per powered USB hub. Camera 2 and 29 were on single power cords.
- A single raspbian image was crated with the included install script, then duplicated to every card. Each card
   then runs the remaining script to personalize it. (piInstall.bash)

CAKE SERVER
- eth0 = 10.9.8.1/24, DHCP Server, NTP Server
- username cake, password cake. Files are uploaded in ~/upload
- Install script asumes dedicated server with private eth0 network. Internet was accessed and shared via wifi.

== USING ==

Inside cakeServer.py set GUIDES=True to print a reference chart on the images to calculate rotation and 
offset in CAM_LIST[].

========