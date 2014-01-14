#!/usr/bin/env python
# (c) 2014 Aaron Land - Digital Blacksmith
import os, time, timeit, socket, random				# Ingredients
os.chdir('/home/cake/upload')						# Work dir

##(O)## GLOBALS

VERS = '3.1.4'

GUIDES=False			## Add guides for calibration
NET_CLASSC = '10.9.8'

SERVER_PORT = 5002
UPLOAD_DIR = '/home/cake/upload/'
SAVE_DIR = '/home/cake/saved/'

CAMERA_PORT = 5001
CAMERA_SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

FRAME_NUM=0

## Camera calibration
##	[ '+clockwise', '+/-xoffset+/-yoffset' ]
CAM_LIST = [
	['+0.0', '+0-0'],	['+0.0', '+0-0'],	['+0.0', '+0-0'],	['+0.0', '+0-0'],	['+0.0', '+0-0'],	# 5
	['+0.0', '+0-0'],	['+0.0', '+0-0'],	['+0.0', '+0-0'],	['+0.0', '+0-0'],	['+0.0', '+0-0'],	# 10
	['+0.0', '+0-0'],	['+0.0', '+0-0'],	['+0.0', '+0-0'],	['+0.0', '+0-0'],	['+0.0', '+0-0'],	# 15
	['+0.0', '+0-0'],	['+0.0', '+0-0'],	['+0.0', '+0-0'],	['+0.0', '+0-0'],	['+0.0', '+0-0'],	# 20
	['+0.0', '+0-0'],	['+0.0', '+0-0'],	['+0.0', '+0-0'],	['+0.0', '+0-0'],	['+0.0', '+0-0'],	# 25
	['+0.0', '+0-0'],	['+0.0', '+0-0'],	['+0.0', '+0-0'],	['+0.0', '+0-0'],	['+0.0', '+0-0'],	# 30
]

##(O)## FUNCTIONS

def cakePrint(msg):
	print '\033[1m' + msg + '\033[0m'

def cakeSleep(zzz):
	time.sleep(zzz - 0.001)

def saveFile(file):
	cakePrint('(S) Saving:' + file)
	cmd = 'cp ' + file + ' ' + SAVE_DIR + time.strftime("m%m-d%d+H%H-M%M-S%S") + '_' + file
	#print cmd
	os.system(cmd)
	
def sendMsg(cam, msg):
	global FRAME_NUM
	if msg == 'FIRE':
		FRAME_NUM += 1
		msg += ' ' + str(FRAME_NUM).zfill(3)
	if msg == 'FINISH' and GUIDES:
		msg += ' guide'
	CAMERA_SOCK.sendto(msg, (NET_CLASSC + '.' + str(cam), CAMERA_PORT))
	#print 'Sent: "' + msg + '" to cam:', str(cam)

def sendMsgAll(msg):
	for c in range(1,len(CAM_LIST)+1):
		sendMsg(c, msg)

def makeFlipbook(zzz=0):
	cakePrint('(F) Making flipbook...')
	time.sleep(zzz)
	## -map_metadata -1
	cmd = 'avconv -i %3d.jpg -r 10 -vcodec libx264 -vprofile high -tune stillimage -pix_fmt yuv420p -s 480x480 -y FLIPBOOK.h264 1>/dev/null 2>/dev/null'
	#print cmd
	os.system(cmd)
	os.system('MP4Box -add FLIPBOOK.h264 -fps 10 OUT.mp4 1>/dev/null 2>/dev/null')

##(O)## PROGRAMS

TIME_START = 0
def program_start(zzz=0):
	global TIME_START, FRAME_NUM
	os.system('rm -f *.jpg *.h264 *.mp4')
	FRAME_NUM = 0
	sendMsgAll('READY')
	cakeSleep(2.0 + zzz)
	cakePrint('\033[32m(P) Program running...')
	TIME_START = timeit.default_timer()


def program_finish(zzz=0):
	global FRAME_NUM, UPLOAD_DIR
	cakePrint('\033[31m(P) Program Finshed!' + ' (' + str(FRAME_NUM) +' frames)')
	cakePrint('\033[33m(t) Time: ' + str(timeit.default_timer() - TIME_START))

	cakeSleep(1.0 + zzz)
	sendMsgAll('FINISH')
	cakePrint('(P) Uploading...')

	count = 0
	while count < FRAME_NUM:
		count = len([name for name in os.listdir('/home/cake/upload/') if name.endswith('.jpg')])
		time.sleep(1)
	cakePrint('\033[33m(t) Time: ' + str(timeit.default_timer() - TIME_START))

	cakePrint('(P) Processing...')
	files_list = os.listdir(".")
	for file_in in files_list:
		if not file_in.endswith('.jpg'): continue
		frame, cam = file_in.split('_')
		cam, end = cam.split('.')
		cam = int(cam.lstrip('0'))

		#cakePrint('(O) Processing: ' + file_in)
		rotate = CAM_LIST[cam-1][0]
		position = CAM_LIST[cam-1][1]
		
		#cakePrint('(O) Rotating...')
		# Rotation takes so long it's faster to do it on the server.
		cmd = 'convert ' + file_in + ' -rotate ' + rotate + ' ' + file_in
		#print cmd
		os.system(cmd)

		#cakePrint('(O) Cropping...')	[Pi prescaling: 0%:1440x1440, 30%:1024x1024] NOT FINAL OUT SIZE
		cmd = 'convert ' + file_in + ' -gravity Center -crop 1024x1024' + position + ' ' + file_in
		#print cmd
		os.system(cmd)

		if GUIDES:
			cakePrint('(G) Adding guides...')
			cmd = 'convert ' + file_in + ' -gravity Center -pointsize 21 -fill "#888888" -draw "text 0,250 \'' + rotate + ':' + position + '\'" -draw "text 0,0 +" -draw "text 100,0 +" -draw "text -100,0 -" -draw "text 0,100 +" -draw "text 0,-100 -" ' + file_in
			print cmd
			os.system(cmd)

		os.system('mv ' + file_in + ' ' + frame + '.jpg')

	cakePrint('\033[33m(t) Time: ' + str(timeit.default_timer() - TIME_START))
	cakePrint('(P) Finshed!')

def program_run_random():
	global TIME_START
	cakePrint('(P) Program: Run Random...')
	reverse = False
	
	## Start Program
	program_start()
	
	## First run Linear
	script_linear_at_time(rev=reverse)
	
	## Randomly run three scripts
	rand_list = ['a', 'b', 'c']
	random.shuffle(rand_list,random.random)
	for f in rand_list:
		reverse = not reverse
		cakeSleep(0.3) ## Cameras 2 and 29 need a bot more time
		if   f == 'a':	script_linear_burst(rev=reverse)
		elif f == 'b':	script_decelaccel_burst(rev=reverse)
		elif f == 'c':	script_decel_freeze_accel(rev=reverse)
	
	## Finish on a freeze
	reverse = not reverse
	cakeSleep(0.3)
	script_all(rev=reverse)

	## Finish Program
	program_finish()

	## Make Flipbook
	makeFlipbook()
	
	## Save File
	saveFile('OUT.mp4')

	## Final program time
	time_stop = timeit.default_timer()
	cakePrint('\033[33m(t) Time: ' + str(time_stop - TIME_START))

##(O)## SCRIPTS

def script_all(rev=False):
	cakePrint('(S) Script: All cameras at once (30f 0sec)')
	list = range(1,len(CAM_LIST)+1)
	if rev==True: list = reversed(list)
	for c in list:
		sendMsg(c, 'FIRE')

def script_linear_at_time(rev=False):
	cakePrint('(S) Script: All cameras linear at frame rate (30f 3sec)')
	list = range(1,len(CAM_LIST)+1)
	if rev==True: list = reversed(list)
	for c in list:
		sendMsg(c, 'FIRE')
		cakeSleep(0.1)

def script_linear_burst(rev=False):
	cakePrint('(S) Script: Linear 1 frame burst @ 5fps (60f 12sec)')
	list = range(1,len(CAM_LIST)+1)
	if rev==True: list = reversed(list)
	for c in list:
		sendMsg(c, 'FIRE')
		cakeSleep(0.2)
		#sendMsg(c, 'FIRE')
		#cakeSleep(0.2)

def script_decelaccel_burst(rev=False):
	cakePrint('(S) Script: Decel -> Burst @ 5fps -> Accel (50f 8sec)')

	if not rev:
		sendMsg(1, 'FIRE');	cakeSleep(0.1)
		sendMsg(2, 'FIRE');	cakeSleep(0.11)
		sendMsg(3, 'FIRE');	cakeSleep(0.12)
		sendMsg(4, 'FIRE');	cakeSleep(0.13)
		sendMsg(5, 'FIRE');	cakeSleep(0.14)
		sendMsg(6, 'FIRE');	cakeSleep(0.15)
		sendMsg(7, 'FIRE');	cakeSleep(0.16)
		sendMsg(8, 'FIRE');	cakeSleep(0.17)
		sendMsg(9, 'FIRE');	cakeSleep(0.18)
		sendMsg(10, 'FIRE');	cakeSleep(0.19)
		sendMsg(11, 'FIRE');	cakeSleep(0.2)

		sendMsg(12, 'FIRE');	cakeSleep(0.2)
		sendMsg(12, 'FIRE');	cakeSleep(0.2)

		sendMsg(13, 'FIRE');	cakeSleep(0.2)
		sendMsg(13, 'FIRE');	cakeSleep(0.2)
		sendMsg(13, 'FIRE');	cakeSleep(0.2)

		sendMsg(14, 'FIRE');	cakeSleep(0.2)
		sendMsg(14, 'FIRE');	cakeSleep(0.2)
		sendMsg(14, 'FIRE');	cakeSleep(0.2)
		sendMsg(14, 'FIRE');	cakeSleep(0.2)

		sendMsg(15, 'FIRE');	cakeSleep(0.2)
		sendMsg(15, 'FIRE');	cakeSleep(0.2)
		sendMsg(15, 'FIRE');	cakeSleep(0.2)
		sendMsg(15, 'FIRE');	cakeSleep(0.2)
		sendMsg(15, 'FIRE');	cakeSleep(0.2)

		sendMsg(16, 'FIRE');	cakeSleep(0.2)
		sendMsg(16, 'FIRE');	cakeSleep(0.2)
		sendMsg(16, 'FIRE');	cakeSleep(0.2)
		sendMsg(16, 'FIRE');	cakeSleep(0.2)
		sendMsg(16, 'FIRE');	cakeSleep(0.2)
	
		sendMsg(17, 'FIRE');	cakeSleep(0.2)
		sendMsg(17, 'FIRE');	cakeSleep(0.2)
		sendMsg(17, 'FIRE');	cakeSleep(0.2)
		sendMsg(17, 'FIRE');	cakeSleep(0.2)

		sendMsg(18, 'FIRE');	cakeSleep(0.2)
		sendMsg(18, 'FIRE');	cakeSleep(0.2)
		sendMsg(18, 'FIRE');	cakeSleep(0.2)

		sendMsg(19, 'FIRE');	cakeSleep(0.2)
		sendMsg(19, 'FIRE');	cakeSleep(0.2)

		sendMsg(20, 'FIRE');	cakeSleep(0.19)
		sendMsg(21, 'FIRE');	cakeSleep(0.18)
		sendMsg(22, 'FIRE');	cakeSleep(0.17)
		sendMsg(23, 'FIRE');	cakeSleep(0.16)
		sendMsg(24, 'FIRE');	cakeSleep(0.15)
		sendMsg(25, 'FIRE');	cakeSleep(0.14)
		sendMsg(26, 'FIRE');	cakeSleep(0.13)
		sendMsg(27, 'FIRE');	cakeSleep(0.12)
		sendMsg(28, 'FIRE');	cakeSleep(0.11)
		sendMsg(29, 'FIRE');	cakeSleep(0.1)
		sendMsg(30, 'FIRE');
	else:
		cakePrint('Reversed...')
		sendMsg(30, 'FIRE');	cakeSleep(0.1)
		sendMsg(29, 'FIRE');	cakeSleep(0.11)
		sendMsg(28, 'FIRE');	cakeSleep(0.12)
		sendMsg(27, 'FIRE');	cakeSleep(0.13)
		sendMsg(26, 'FIRE');	cakeSleep(0.14)
		sendMsg(25, 'FIRE');	cakeSleep(0.15)
		sendMsg(24, 'FIRE');	cakeSleep(0.16)
		sendMsg(23, 'FIRE');	cakeSleep(0.17)
		sendMsg(22, 'FIRE');	cakeSleep(0.18)
		sendMsg(21, 'FIRE');	cakeSleep(0.19)
		sendMsg(20, 'FIRE');	cakeSleep(0.2)

		sendMsg(19, 'FIRE');	cakeSleep(0.2)
		sendMsg(19, 'FIRE');	cakeSleep(0.2)

		sendMsg(18, 'FIRE');	cakeSleep(0.2)
		sendMsg(18, 'FIRE');	cakeSleep(0.2)
		sendMsg(18, 'FIRE');	cakeSleep(0.2)

		sendMsg(17, 'FIRE');	cakeSleep(0.2)
		sendMsg(17, 'FIRE');	cakeSleep(0.2)
		sendMsg(17, 'FIRE');	cakeSleep(0.2)
		sendMsg(17, 'FIRE');	cakeSleep(0.2)

		sendMsg(16, 'FIRE');	cakeSleep(0.2)
		sendMsg(16, 'FIRE');	cakeSleep(0.2)
		sendMsg(16, 'FIRE');	cakeSleep(0.2)
		sendMsg(16, 'FIRE');	cakeSleep(0.2)
		sendMsg(16, 'FIRE');	cakeSleep(0.2)

		sendMsg(15, 'FIRE');	cakeSleep(0.2)
		sendMsg(15, 'FIRE');	cakeSleep(0.2)
		sendMsg(15, 'FIRE');	cakeSleep(0.2)
		sendMsg(15, 'FIRE');	cakeSleep(0.2)
		sendMsg(15, 'FIRE');	cakeSleep(0.2)
	
		sendMsg(14, 'FIRE');	cakeSleep(0.2)
		sendMsg(14, 'FIRE');	cakeSleep(0.2)
		sendMsg(14, 'FIRE');	cakeSleep(0.2)
		sendMsg(14, 'FIRE');	cakeSleep(0.2)

		sendMsg(13, 'FIRE');	cakeSleep(0.2)
		sendMsg(13, 'FIRE');	cakeSleep(0.2)
		sendMsg(13, 'FIRE');	cakeSleep(0.2)

		sendMsg(12, 'FIRE');	cakeSleep(0.2)
		sendMsg(12, 'FIRE');	cakeSleep(0.2)

		sendMsg(11, 'FIRE');	cakeSleep(0.19)
		sendMsg(10, 'FIRE');	cakeSleep(0.18)
		sendMsg(9, 'FIRE');	cakeSleep(0.17)
		sendMsg(8, 'FIRE');	cakeSleep(0.16)
		sendMsg(7, 'FIRE');	cakeSleep(0.15)
		sendMsg(6, 'FIRE');	cakeSleep(0.14)
		sendMsg(5, 'FIRE');	cakeSleep(0.13)
		sendMsg(4, 'FIRE');	cakeSleep(0.12)
		sendMsg(3, 'FIRE');	cakeSleep(0.11)
		sendMsg(2, 'FIRE');	cakeSleep(0.1)
		sendMsg(1, 'FIRE');

def script_decel_freeze_accel(rev=False):
	cakePrint('(S) Script: Decel -> Freeze -> Accel [x^2 / 1000] (30f 1sec)')

	if not rev:
		sendMsg(1, 'FIRE');	cakeSleep(0.09)
		sendMsg(2, 'FIRE');	cakeSleep(0.072)
		sendMsg(3, 'FIRE');	cakeSleep(0.057)
		sendMsg(4, 'FIRE');	cakeSleep(0.044)
		sendMsg(5, 'FIRE');	cakeSleep(0.032)
		sendMsg(6, 'FIRE');	cakeSleep(0.022)
		sendMsg(7, 'FIRE');	cakeSleep(0.014)
		sendMsg(8, 'FIRE');	cakeSleep(0.008)
		sendMsg(9, 'FIRE');	cakeSleep(0.003)
		sendMsg(10, 'FIRE');	cakeSleep(0.001)
		sendMsg(11, 'FIRE')
		sendMsg(12, 'FIRE')
		sendMsg(13, 'FIRE')
		sendMsg(14, 'FIRE')
		sendMsg(15, 'FIRE')
		sendMsg(16, 'FIRE')
		sendMsg(17, 'FIRE')
		sendMsg(18, 'FIRE')
		sendMsg(19, 'FIRE')
		sendMsg(20, 'FIRE');	cakeSleep(0.001)
		sendMsg(21, 'FIRE');	cakeSleep(0.003)
		sendMsg(22, 'FIRE');	cakeSleep(0.008)
		sendMsg(23, 'FIRE');	cakeSleep(0.014)
		sendMsg(24, 'FIRE');	cakeSleep(0.022)
		sendMsg(25, 'FIRE');	cakeSleep(0.032)
		sendMsg(26, 'FIRE');	cakeSleep(0.044)
		sendMsg(27, 'FIRE');	cakeSleep(0.057)
		sendMsg(28, 'FIRE');	cakeSleep(0.072)
		sendMsg(29, 'FIRE');	cakeSleep(0.09)
		sendMsg(30, 'FIRE')
	else:
		sendMsg(30, 'FIRE');	cakeSleep(0.09)
		sendMsg(29, 'FIRE');	cakeSleep(0.072)
		sendMsg(28, 'FIRE');	cakeSleep(0.057)
		sendMsg(27, 'FIRE');	cakeSleep(0.044)
		sendMsg(26, 'FIRE');	cakeSleep(0.032)
		sendMsg(25, 'FIRE');	cakeSleep(0.022)
		sendMsg(24, 'FIRE');	cakeSleep(0.014)
		sendMsg(23, 'FIRE');	cakeSleep(0.008)
		sendMsg(22, 'FIRE');	cakeSleep(0.003)
		sendMsg(21, 'FIRE');	cakeSleep(0.001)
		sendMsg(20, 'FIRE')
		sendMsg(19, 'FIRE')
		sendMsg(18, 'FIRE')
		sendMsg(17, 'FIRE')
		sendMsg(16, 'FIRE')
		sendMsg(15, 'FIRE')
		sendMsg(14, 'FIRE')
		sendMsg(13, 'FIRE')
		sendMsg(12, 'FIRE')
		sendMsg(11, 'FIRE');	cakeSleep(0.001)
		sendMsg(10, 'FIRE');	cakeSleep(0.003)
		sendMsg(9, 'FIRE');	cakeSleep(0.008)
		sendMsg(8, 'FIRE');	cakeSleep(0.014)
		sendMsg(7, 'FIRE');	cakeSleep(0.022)
		sendMsg(6, 'FIRE');	cakeSleep(0.032)
		sendMsg(5, 'FIRE');	cakeSleep(0.044)
		sendMsg(4, 'FIRE');	cakeSleep(0.057)
		sendMsg(3, 'FIRE');	cakeSleep(0.072)
		sendMsg(2, 'FIRE');	cakeSleep(0.09)
		sendMsg(1, 'FIRE')

def script_linear_zig_zag():
	cakePrint('(S) Script: Linear zig-zag (12sec)')
	time.sleep(10)

	for x in range(0,3):
		sendMsg(1, 'FIRE')
		cakeSleep(0.3)
		for c in range(2, 30):
			sendMsg(c, 'FIRE')
			cakeSleep(0.1)
		sendMsg(30, 'FIRE')
		cakeSleep(0.3)
		for c in reversed(range(2, 30)):
			sendMsg(c, 'FIRE')
			cakeSleep(0.1)

##(O)## RUNLOOP

cakePrint('(*) piBullet Server' + VERS + ' ##')
while True:
	print '\033[1m##(*) Menu:'
	print 'Programs:            Send to ALL:        Server:'
	print ' r : Run Random       1 : ROLLCALL        F : Make Flipbook'
	print '                      2 : READY           Q : QUIT'
	print 'Scripts:              3 : FIRE'
	print ' a : All cameras      4 : FINISH'
	print ' l : Linear @ time'
	print ' b : Linear burst    up : UPDATE'
	print ' d : (burst)(burst)  UP : FORCE-UPDATE'
	print ' s : (--)            RS : RESTART'
	print ' z : zig-zag         SD : SHUTDOWN \033[0m'
	
	choice = raw_input('Do what now?: ')

	if choice == 'r':
		program_run_random()
	
	elif choice == 'a':
		script_all()
	elif choice == 'l':
		script_linear_at_time()
	elif choice == 'b':
		script_linear_burst()
	elif choice == 'd':
		script_decelaccel_burst()
	elif choice == 's':
		script_decel_freeze_accel()
	elif choice == 'z':
		script_linear_zig_zag()

	elif choice == '1': 
		cakePrint('(#) Checking in...')
		server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server.bind(('0.0.0.0', SERVER_PORT))
		server.settimeout(0.05)
		for c in range(1,len(CAM_LIST)+1):
			sendMsg(c, 'ROLLCALL')
			try:
				data = server.recv(128)
				cakePrint('Camera: ' + str(c) + ' = \033[92m' + data)
			except socket.error, e:
				cakePrint('Camera: ' + str(c) + ' = \033[31mOFFLINE')
		server.close()
	elif choice == '2':
		cakePrint('(#) Sending READY...')
		program_start()
	elif choice == '3':
		cakePrint('(#) Fire all...')
		sendMsgAll('FIRE')
	elif choice == '4':
		cakePrint('(#) Sending FINISH...')
		program_finish()

	elif choice == 'up':
		# Self update the client
		cakePrint('(&) Updating...')
		sendMsgAll('UPDATE')
	elif choice == 'UP':
		# Force update the client
		cakePrint('(&) Force Updating...')
		os.chdir('/home/cake/')
		for c in range(1,len(CAM_LIST)+1):
			cmd = 'echo "put piBullet.py" | sftp -b- pi@' + NET_CLASSC + '.' + str(c)
			print cmd
			os.system(cmd)
			cakePrint('(&) ' + str(c) + ' done.')
		quit()
	elif choice == 'RS':
		cakePrint('(&) Restating...')
		sendMsgAll('RESTART')
	elif choice == 'SD':
		cakePrint('(&) Shutting down...')
		sendMsgAll('SHUTDOWN')

	elif choice == 'F':
		makeFlipbook()
	elif choice == 'q' or choice == 'Q':
		break
	else:
		cakePrint('\033[31mERROR in choice:' + choice)

##(O)## SHUTTING DOWN

cakePrint('##(*) DONE ##')