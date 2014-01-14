#!/usr/bin/env python
#(c) 2014 Aaron Land - Digital Blacksmith
# raspifastcamd ( https://bitbucket.org/niklas_rother/rasperry-pi-userland/raw/master/host_applications/linux/apps/raspicam/raspifastcamd_scripts )

import os, sys, time, signal, subprocess, socket	# Ingredients
if os.fork() > 0: sys.exit(0)				# Daemonize
os.chdir('/dev/shm')					# Work in ram disk
os.nice(-18)						# Work harder
sys.stdout = open('/home/pi/piBullet.log', 'w')		# Log file
print '##(O) piBullet Camera ##'

##(O)## GLOBALS

VERS = 'v3.1.4'

SAVE_DIR = ''
#SAVE_DIR = '/home/pi/saved/'	# Change to save captured images

LISTEN_PORT = 5001
LISTEN = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
LISTEN.bind(('0.0.0.0', LISTEN_PORT))

SERVER_ADDY = '10.9.8.250'
SERVER_PORT = 5002
SERVER_DIR = '/home/cake/upload'

PROCESS = 0
FRAMES_LIST = []
# Determine ID from the last didget of the IP address
MY_ID = subprocess.check_output("printf '%03d' $(ip addr show eth0 |  grep 'inet ' | awk '{print $2}' | cut -d. -f4 | cut -d/ -f1)", shell=True)

##(O)## FUNCTIONS

def piPrint(msg):
	print msg
	sys.stdout.flush()

##(O)## RUNLOOP

piPrint('(O) ' + VERS + ' Running as ID: ' + MY_ID + ' PID: ' + str(os.getpid()))
while True:
	piPrint('(O) Listening on:' + str(LISTEN_PORT))
	data, addy = LISTEN.recvfrom(128)
	if not data: break
	
	# Receive task
	command = var1 = ''
	try:
		command, var1 = data.split(" ")
	except ValueError:
		command = data

	# Process task
	if command == 'ROLLCALL':
		# Tell the server we're ready
		server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server.sendto('ONLINE ' + VERS, (SERVER_ADDY, SERVER_PORT))
		server.close()
		piPrint('(O) Server checked in')

	elif command == 'READY':
		# Begin camera app
		os.system('rm -f *.jpg')
		FRAMES_LIST = []
		cmd = '/home/pi/raspifastcamd -ISO 100 -awb sun -ex sports -o %02d.jpg'
		print cmd
		PROCESS = subprocess.Popen('exec ' + cmd, shell=True)
		piPrint('(O) Ready! pid=' + str(PROCESS.pid))

	elif command == 'FIRE':
		# Capture picture
		PROCESS.send_signal(signal.SIGUSR1)
		piPrint('(O) Captured: ' + var1)
		FRAMES_LIST.append(var1)

	elif command == 'FINISH':
		piPrint('(O) Finished...')
		time.sleep(1) # Save the last file just in case
		if PROCESS:
			PROCESS.kill()
			PROCESS = 0

		# Process files then uplodad them
		for i,n in enumerate(FRAMES_LIST):
			file_in = str(i).zfill(2) + '.jpg'
			file_out = str(n) + '_' + MY_ID + '.jpg'
			piPrint('(O) Processing: ' + file_in + ' -> ' + file_out)
			
			if SAVE_DIR:
				piPrint('(S) Saving:' + file_in)
				cmd = 'cp ' + file_in + ' ' + SAVE_DIR + time.strftime("m%m-d%d+H%H-M%M-S%S") + '_' + file_in
				print cmd
				os.system(cmd)
			
			if var1 == 'guide': # For alignment
				piPrint('(G) Adding center marker...')
				cmd = 'convert ' + file_in + ' -gravity Center -pointsize 64 -fill "#FF4444" -draw "text 0,0 +" -fill "#888888" -draw "text 850,500 FR' + MY_ID + '" ' + file_in
				print cmd
				os.system(cmd)
		
			piPrint('(O) Resize 30% before sending...') # -flip -flop OR -rotate +180
			cmd = 'convert ' + file_in + ' -resize 30% ' + file_in
			print cmd
			os.system(cmd)
			
			cmd = 'mv -n ' + file_in + ' ' + file_out
			print cmd
			os.system(cmd)

		piPrint('(O) Uploading...')
		cmd = 'lftp -u cake,cake -e "set -a xfer:clobber true; mirror -R . ' + SERVER_DIR + '; quit" ' +  SERVER_ADDY
		print cmd
		os.system(cmd)

	elif command == 'CLICK':
		# Take a still
		cmd = '/usr/bin/raspistill -ISO 100 -awb sun -ex sports -n -o ' + var1 + '.jpg'
		print cmd
		print subprocess.check_output(cmd, shell=True)

	elif command == 'UPDATE':
		# Self update
		piPrint('(O) Updating...')
		os.chdir('/home/pi')
		cmd = 'lftp -u cake,cake -e "set -a xfer:clobber true; get piBullet.py; quit" ' + SERVER_ADDY + '; sudo chown pi:pi piBullet.py'
		print cmd
		os.system(cmd)
		os.system('sudo reboot')

	elif command == 'RESTART':
		piPrint('(O) Restarting...')
		os.system('sudo reboot')

	elif command == 'SHUTDOWN':
		piPrint('(O) Shutting Down...')
		os.system('sudo shutdown -h now')

	else:
		piPrint('ERROR in packet: "' + command + '" "' + var1 + '"')

##(O)## SHUTTING DOWN

LISTEN.close()
print '##(O) Quit ##'