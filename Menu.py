from PIL import ImageFont, ImageDraw
from luma.core.render import canvas
import math

class Menu:

    index = 0

    def __init__(self, device, encoder, title, items):
        self.device = device.device
        self.encoder = encoder
        self.encoder.set_click_handler(self.click_handler)
        self.title = title
        self.items = items
        self.items_per_page = 5

    def _invert(self, draw, x, y, text):
        # font = ImageFont.load_default()
        draw.rectangle((0, y, self.device.width, y+10), outline=255, fill=255)
        draw.text((x, y), text, outline=0, fill="black")

    def draw_menu(self):
        
        # font = ImageFont.load_default()

        with canvas(self.device) as draw:
            self._draw_title(draw)
            
            # Limit items on the screen
            if (len(self.items) > self.items_per_page):
                mid = int(math.ceil(self.items_per_page / 2.0))
                start = 0 if self.index < mid else self.index - mid
            else:
                start = 0

            # if (len(self.items) > self.items_per_page):
            #     end = start + self.items_per_page
            # else:
            #     end = len(self.items)

            end = len(self.items)

            row = 1
            for i in range(start, end):
                if( i == self.index):
                    self._invert(draw, 2, row*10, self.items[i])
                else:
                    draw.text((2, row*10), self.items[i], fill="white")
                
                row += 1

    def _draw_title(self, draw):
        draw.text((2, 0), self.title, fill="white")
        draw.line((0, 10, self.device.width, 10), fill="white")

    def set_index(self, count):
        if (self.index + count <= 0):
            self.index = 0
        elif (self.index + count > len(self.items) - 1):
            self.index = len(self.items) - 1
        else:
            self.index += count

    def click_handler(self):
        print 'Menu Click: ' + str(self.items[self.index])