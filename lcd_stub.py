
class LCD(object):
    def __init__(self):
        self.width = 128
        self.height = 128

    def LCD_Init(self):
        pass

    def LCD_Clear(self):
        pass

    def LCD_ShowImage(self, image):
        image.save("image.png")
