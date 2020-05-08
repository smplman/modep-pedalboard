from RPi import GPIO
from time import sleep

import threading

Enc_A = 15  			# Encoder input A: input pin 15 
Enc_B = 13  			# Encoder input B: input pin 13 
Enc_SW = 11             # Encoder click: input pin 11

class Encoder:

	lock_rotary = threading.Lock()
	rotary_counter = 0
	index = 0
	current_A = 1
	current_B = 1

	def __init__(self):
		# define the Encoder switch inputs
		GPIO.setup(Enc_A, GPIO.IN) 				
		GPIO.setup(Enc_B, GPIO.IN)
		GPIO.setup(Enc_SW, GPIO.IN)
		# setup callback thread for the A and B encoder 
		# use interrupts for all inputs
		GPIO.add_event_detect(Enc_A, GPIO.RISING, callback=self._rotary_interrupt) 				# NO bouncetime 
		GPIO.add_event_detect(Enc_B, GPIO.RISING, callback=self._rotary_interrupt) 				# NO bouncetime 
		GPIO.add_event_detect(Enc_SW, GPIO.FALLING , callback=self._rotary_click_interrupt, bouncetime=300)

	# Rotarty encoder interrupt:
	# this one is called for both inputs from rotary switch (A and B)
	def _rotary_interrupt(self, A_or_B):
														# read both of the switches
		Switch_A = GPIO.input(Enc_A)
		Switch_B = GPIO.input(Enc_B)
														# now check if state of A or B has changed
														# if not that means that bouncing caused it
		if self.current_A == Switch_A and self.current_B == Switch_B:		# Same interrupt as before (Bouncing)?
			return										# ignore interrupt!

		self.current_A = Switch_A								# remember new state
		self.current_B = Switch_B								# for next bouncing check


		if (Switch_A and Switch_B):						# Both one active? Yes -> end of sequence
			self.lock_rotary.acquire()						# get lock 
			if A_or_B == Enc_B:							# Turning direction depends on 
				self.rotary_counter += 1						# which input gave last interrupt
			else:										# so depending on direction either
				self.rotary_counter -= 1						# increase or decrease counter
			self.lock_rotary.release()						# and release lock
		return											# THAT'S IT

	def _rotary_click_interrupt(self, channel):  
		self.click_handler()

	def read(self):
		sleep(0.1)					
												
		self.lock_rotary.acquire()				    # get lock for rotary switch
		counter = self.rotary_counter			    # get counter value
		self.rotary_counter = 0						# RESET IT TO 0
		self.lock_rotary.release()					# and release lock

		return counter

	def set_click_handler(self, handler):
		self.click_handler = handler