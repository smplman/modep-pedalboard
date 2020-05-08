from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1309

from RPi import GPIO
from time import sleep

RESET = 7               # OLED Reset pin 7

class OledDisplay:

	def __init__(self):
		# OLED Reset pin
		GPIO.setup(RESET, GPIO.OUT)

		self._reset()
		
		serial = i2c(port=1, address=0x3C)
		self.device = ssd1309(serial)

	def _reset(self):
		print 'Reset Oled'
		# rest low then high
		GPIO.output(RESET, GPIO.LOW)
		sleep(0.200)
		GPIO.output(RESET, GPIO.HIGH)

	def draw(self):
		with canvas(self.device) as draw:
			return draw
