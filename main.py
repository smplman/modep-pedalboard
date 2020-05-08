from RPi import GPIO

from Oled import OledDisplay
from Encoder import Encoder
from Menu import Menu

def init():
    global display, encoder, settings_menu

    GPIO.setwarnings(True)
    GPIO.setmode(GPIO.BOARD)

    encoder = Encoder()
    display = OledDisplay()

    settings_menu_options = {
        'title': 'Settings'
        'items': [
            {
                'title':''
            }
        ]

    }

    # create settings menu
    settings_menu = Menu(display, encoder, 'Settings', ['Effects', 'Banks', 'Current Pedalboard', 'Volume and Gains', 'Headphone', 'Bluetooth'])

def main():
    init()

    while True :
        settings_menu.set_index(encoder.read())
        settings_menu.draw_menu()

main()
GPIO.cleanup()