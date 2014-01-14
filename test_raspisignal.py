#!/usr/bin/env python
#(c) 2013 Aaron Land - Digital Blacksmith

## raspifastcamd and raspistill test script

import os, time, timeit, signal, subprocess
os.chdir('/dev/shm')
os.system('rm -f *.jpg')

## GLOBALS ##
FRAMES = 30
SETTINGS = ' -awb sun -ex sports -mm backlit'

## raspifastcamd v1.2 ##
SLEEP = 0.29;
cmd = '/home/pi/raspifastcamd -o %03d.jpg -ISO 100' + SETTINGS
## Captured 30 images in 8.72sec at 3.44fps

## raspistill v1.3.5 ##
#SLEEP = 0.65;
#cmd = '/usr/bin/raspistill --signal -o %d.jpg -th none -t 60000 -ss 32000' + SETTINGS
## Captured 30 images in 20.73sec at 1.45fps

print cmd
PROCESS = subprocess.Popen('exec ' + cmd, shell=True)
time.sleep(2)	#let it auto adjust

TIME_START = timeit.default_timer()
for x in range(0,FRAMES):
	PROCESS.send_signal(signal.SIGUSR1)
#	print(str(x))
	time.sleep(SLEEP)
TIME_STOP = timeit.default_timer()

PROCESS.kill()
print("Captured %d images in %.2fsec at %.2ffps" % (FRAMES, TIME_STOP - TIME_START, FRAMES/(TIME_STOP - TIME_START)))
os.system('ls -lh /dev/shm/')