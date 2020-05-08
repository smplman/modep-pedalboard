from PIL import ImageFont, ImageDraw
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1309

from RPi import GPIO
from time import sleep

import requests

# Use reset pin to start the oled
reset = 7
GPIO.setmode(GPIO.BOARD)
GPIO.setup(reset, GPIO.OUT)
# rest low then high
GPIO.output(reset, GPIO.LOW)
sleep(0.100)
GPIO.output(reset, GPIO.HIGH)

# Rotarty Encoder
clk = 15
dt = 13
sw = 11
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)
clkLastState = GPIO.input(clk)

# rev.1 users set port=0
# substitute spi(device=0, port=0) below if using that interface
serial = i2c(port=1, address=0x3C) # 0x3C or 0x3D

# substitute ssd1331(...) or sh1106(...) below if using that device
device = ssd1309(serial)

# get effects
URL = "http://127.0.0.1/effect/list"
r = requests.get(url = URL)

data = r.json()

counter = 0

# while True:
#     with canvas(device) as draw:
#         # draw.rectangle(device.bounding_box, outline="white", fill="black")
#         # draw.text((0, 0), data[0]['name'], fill="white")
#         # draw.text((0, 10), data[1]['name'], fill="white")

#         y = 0

#         for effect in data:
#             draw.text((0, y), effect['name'], fill="white")
#             y += 10

def invert(draw,x,y,text):
    font = ImageFont.load_default()
    draw.rectangle((x, y, x+120, y+10), outline=255, fill=255)
    draw.text((x, y), text, font=font, outline=0,fill="black")
	
# Box and text rendered in portrait mode
def menu(device, draw, menustr,index):
    global menuindex
    font = ImageFont.load_default()
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    for i in range(len(menustr)):
        if( i == index):
            menuindex = i
            invert(draw, 2, i*10, menustr[i]['name'])
        else:
		    draw.text((2, i*10), menustr[i]['name'], font=font, fill="white")

def sw_callback(channel):  
    global menuindex
    global insubmenu

    strval = data[menuindex]['name']
    print strval
    # menu_operation(strval)

def rotary_callback(channel):  
    global clkLastState
    global counter
    try:
        clkState = GPIO.input(clk)
        if clkState != clkLastState:
            dtState = GPIO.input(dt)
            print "dtState " + str(dtState)
            print "clkState " + str(clkState)
            if dtState != clkState:
                    counter += 1
            else:
                    counter -= 1
            print counter
            with canvas(device) as draw:
                menu(device, draw, data,counter%7)
        clkLastState = clkState
    finally:
                print "Ending"

GPIO.add_event_detect(clk, GPIO.FALLING , callback=rotary_callback, bouncetime=100)  
GPIO.add_event_detect(dt, GPIO.FALLING , callback=rotary_callback, bouncetime=100)  
GPIO.add_event_detect(sw, GPIO.FALLING , callback=sw_callback, bouncetime=300)  
raw_input("Enter anything")
GPIO.cleanup()