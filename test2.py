# Encoder credit to hrvoje https://www.raspberrypi.org/forums/memberlist.php?mode=viewprofile&u=181316&sid=e190f15e1323ec098b6678175b3a0dcb
# https://www.raspberrypi.org/forums/viewtopic.php?t=140250

from PIL import ImageFont, ImageDraw
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1309

from RPi import GPIO
from time import sleep

import requests
import threading

						# GPIO Ports
Enc_A = 15  			# Encoder input A: input pin 15 
Enc_B = 13  			# Encoder input B: input pin 13 
Enc_SW = 11             # Encoder click: input pin 11
RESET = 7               # OLED Reset pin 7

Rotary_counter = 0  			# Start counting from 0
Current_A = 1					# Assume that rotary switch is not 
Current_B = 1					# moving while we init software

LockRotary = threading.Lock()		# create lock for rotary switch
	

# initialize interrupt handlers
def init():
	global Oled_Device, Effects_Data

	GPIO.setwarnings(True)
	GPIO.setmode(GPIO.BOARD)				# Use Board mode
	
											# define the Encoder switch inputs
	GPIO.setup(Enc_A, GPIO.IN) 				
	GPIO.setup(Enc_B, GPIO.IN)
	GPIO.setup(Enc_SW, GPIO.IN)
											# setup callback thread for the A and B encoder 
											# use interrupts for all inputs
	GPIO.add_event_detect(Enc_A, GPIO.RISING, callback=rotary_interrupt) 				# NO bouncetime 
	GPIO.add_event_detect(Enc_B, GPIO.RISING, callback=rotary_interrupt) 				# NO bouncetime 
	GPIO.add_event_detect(Enc_SW, GPIO.FALLING , callback=rotary_click_interrupt)

	# get effects
	URL = "http://127.0.0.1/effect/list"
	r = requests.get(url = URL)
	Effects_Data = r.json()

	# OLED Reset
	GPIO.setup(RESET, GPIO.OUT)
	# rest low then high
	GPIO.output(RESET, GPIO.LOW)
	sleep(0.100)
	GPIO.output(RESET, GPIO.HIGH)

	serial = i2c(port=1, address=0x3C)
	Oled_Device = ssd1309(serial)

	# Draw initial menu
	with canvas(Oled_Device) as draw:
		draw_menu(Oled_Device, draw, Effects_Data, 0)
	return



# Rotarty encoder interrupt:
# this one is called for both inputs from rotary switch (A and B)
def rotary_interrupt(A_or_B):
	global Rotary_counter, Current_A, Current_B, LockRotary
													# read both of the switches
	Switch_A = GPIO.input(Enc_A)
	Switch_B = GPIO.input(Enc_B)
													# now check if state of A or B has changed
													# if not that means that bouncing caused it
	if Current_A == Switch_A and Current_B == Switch_B:		# Same interrupt as before (Bouncing)?
		return										# ignore interrupt!

	Current_A = Switch_A								# remember new state
	Current_B = Switch_B								# for next bouncing check


	if (Switch_A and Switch_B):						# Both one active? Yes -> end of sequence
		LockRotary.acquire()						# get lock 
		if A_or_B == Enc_B:							# Turning direction depends on 
			Rotary_counter += 1						# which input gave last interrupt
		else:										# so depending on direction either
			Rotary_counter -= 1						# increase or decrease counter
		LockRotary.release()						# and release lock
	return											# THAT'S IT

def rotary_click_interrupt(channel):  

	# strval = data[menuindex]['name']
	# print strval
	print channel
	# menu_operation(strval)

def invert(draw,x,y,text):
    font = ImageFont.load_default()
    draw.rectangle((x, y, x+120, y+10), outline=255, fill=255)
    draw.text((x, y), text, font=font, outline=0, fill="black")

def draw_menu(device, draw, menu_items, index):
	global menuindex
	font = ImageFont.load_default()
	draw.rectangle(device.bounding_box, outline="white", fill="black")
	print "index: " + str(index)
	# page = index % 6
	# print page
	start = 0 if index < 3 else index - 3
	# end = start + 6 if len(menu_items) else 
	print "start: " + str(start)
	# for i in range(len(menu_items)):
	row = 0
	for i in range(start, start + 6):
		print "item: " + str(i) + " " + menu_items[i]['name']
		if( i == index):
			menuindex = i
			invert(draw, 2, row*10, menu_items[i]['name'])
		else:
			draw.text((2, row*10), menu_items[i]['name'], font=font, fill="white")
		
		row += 1

		# only draw 5 menu items at a time
		# if(i >= 5):
		# 	return

	print ""

# Main loop. Demonstrate reading, direction and speed of turning left/rignt
def main():
	global Rotary_counter, LockRotary
	

	Index = 0									# Current Index	
	NewCounter = 0								# for faster reading with locks
						

	init()										# Init interrupts, GPIO, ...
				
	while True :								# start test 
		sleep(0.1)								# sleep 100 msec
		
												# because of threading make sure no thread
												# changes value until we get them
												# and reset them
												
		LockRotary.acquire()					# get lock for rotary switch
		NewCounter = Rotary_counter			# get counter value
		Rotary_counter = 0						# RESET IT TO 0
		LockRotary.release()					# and release lock
					
		if (NewCounter !=0):					# Counter has CHANGED
			Index = Index + NewCounter*abs(NewCounter)	# Decrease or increase Index 
			if Index < 0:						# limit Index to 0...100
				Index = 0
			if Index > len(Effects_Data):					# limit to number of items
				Index = len(Effects_Data)

			# if past multiple of 6 redraw the menu
			
			with canvas(Oled_Device) as draw:
				draw_menu(Oled_Device, draw, Effects_Data, Index)
			# print NewCounter, Index			# some test print
											


# start main demo function
main()
