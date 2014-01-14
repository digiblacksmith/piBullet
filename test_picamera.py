#!/usr/bin/env python
#(c) 2013 Aaron Land - Digital Blacksmith

## picamera test script

import os, sys, time
import picamera

os.chdir('/run/shm')
os.system('rm -f *.jpg')
#os.nice(-19)

FRAMES = 30
RESLIST = [(2592, 1944), (1920,1080), (1280,720), (1024,768), (640,480)]

PREVIEWPORT = True
#(2592, 1944) Captured 30 images at 6.07fps
#(1920, 1080) Captured 30 images at 9.45fps
#(1280, 720) Captured 30 images at 9.54fps
#(1024, 768) Captured 30 images at 9.56fps
#(640, 480) Captured 30 images at 9.61fps

#PREVIEWPORT = False
#(2592, 1944) Captured 30 images at 1.17fps
#(1920, 1080) Captured 30 images at 1.45fps
#(1280, 720) Captured 30 images at 1.51fps
#(1024, 768) Captured 30 images at 1.52fps
#(640, 480) Captured 30 images at 1.53fps

with picamera.PiCamera() as camera:
	for res in RESLIST:
		sys.stdout.write(str(res) + ' ')
		
		camera.resolution = res
	#	camera.preview_window = (0, 0, 1920, 1080)
		
		camera.ISO = 100
		camera.awb_mode = 'tungsten'
		camera.exposure_compensation = 0
		#camera.exposure_mode = 'fixedfps'
		camera.meter_mode = 'spot'
		#camera.image_effect = 'none'
		#camera.shutter_speed(30000)
		#camera.raw_format(yuv|rgb)

		if PREVIEWPORT:
			camera.framerate = 10
			camera.start_preview()
			time.sleep(2)

		start = time.time()
		camera.capture_sequence([
			'image%02d.jpg' % i
			for i in range(FRAMES)
			], use_video_port=PREVIEWPORT)
		finish = time.time()
		
		if PREVIEWPORT:
			time.sleep(2)
			camera.stop_preview()
		
		print("Captured %d images at %.2ffps" % (FRAMES, FRAMES/(finish - start)))
		time.sleep(2)