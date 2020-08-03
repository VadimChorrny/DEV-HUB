import os
from random import sample, choice, randint
from PIL import Image, ImageDraw, ImageFont

captcha_native = "captcha_files"
plate_side = 256
gap = 16
num = 6

class Component:
    def __init__(self, _dir):
        self.image = Image.open(_dir).convert("RGBA")
    
    def transform(self, index=0):
        sq_side = min(*self.image.size)
        self.image = self.image.crop((0, 0, sq_side, sq_side))
        self.image = self.image.resize((plate_side, plate_side))

        digit = Image.new("RGBA", (plate_side, plate_side))
        draw = ImageDraw.Draw(digit)
        size = plate_side // 2
        luc = (plate_side // 2 - 3 * size // 8, plate_side // 2 - 2 * size // 3)
        font = ImageFont.truetype("fonts/arial.ttf", size=size)
        draw.text(luc, f"{index + 1}", fill=(0, 0, 0, 150), font=font)

        self.image = Image.alpha_composite(self.image, digit)


class CAPTCHA_gen:
    def __init__(self):
        self.dirs = [f"{captcha_native}/{el}" for el in sample(os.listdir(captcha_native), num)]
        self.index = randint(0, num - 1)
        self.answer = self.dirs[self.index].rsplit("/", maxsplit=1)[1]
        self.dirs = [f"{folder}/{choice(os.listdir(folder))}" for folder in self.dirs]
    
    def merge_images(self):
        _6_plates = Image.new("RGBA", (plate_side * 3 + gap * 2, plate_side * 2 + gap))
        for i, d in enumerate(self.dirs):
            peace = Component(d)
            peace.transform(i)
            ulc = (i % 3 * (plate_side + gap), i // 3 * (plate_side + gap))
            _6_plates.paste(peace.image, ulc)
        _6_plates.save("captcha_test.png", "PNG")


cg = CAPTCHA_gen()
cg.merge_images()
print(cg.answer, cg.index)