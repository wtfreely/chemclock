"""

Thanks to Rob Weber for making omni-epd.
It sure made dealing with this a lot easier.

"""

import os
import sys
import random
import pubchempy as pcp
from omni_epd import displayfactory, EPDNotFoundError
from PIL import Image, ImageDraw, ImageFont


"""

Be sure to include omni-epd.ini in local folder,
as it is critical for adjusting rotation and other post-processing.

"""

try:
    epd = displayfactory.load_display_driver()
except EPDNotFoundError:
    print("Couldn't find your display")
    sys.exit()

"""
Here's the logic:
Pubchem seems to have a list of chemicals, and each one has a unique "CID" (compound ID?).
I think this is a chemical ID, and I think this list is continuous and also extremely large.
Therefore, it stands to reason that we can pick a random number between 1 and (something huge) and that the API would grab *something*.
And if it doesn't just try again.

def download(outformat, path, identifier, namespace='cid', domain='compound', operation=None, searchtype=None,
             overwrite=False, **kwargs):
    Format can be  XML, ASNT/B, JSON, SDF, CSV, PNG, TXT.

"""

def get_chem(min, max):
    n = random.randint(min, max)
    good_chem = False
    while good_chem == False:
        try:
            c = pcp.Compound.from_cid(n)
            formula = c.molecular_formula
            name = c.iupac_name
            pcp.download('PNG', 'chem.png', n, overwrite=True, size=400)
            good_chem = True
            return formula, name
        except Exception as e:
            print(e)
            good_chem = False
            print("bad chem")

"""
So, pubchems output is a little janky, and off center.
To correct for this, I am just going to clip the image to it's opaque pixels, so we can center that element.
Let's convert all the white pixels to alpha, by looping through the pixel data (RGB) and converting white to transparent,
And everything else becomes white.
Then we can get the bounding box of non-alpha pixels, and then crop to that bounding box.
"""

def image_processing(image):
    img = Image.open(image)
    img = img.convert("RGBA")
    pixels = img.getdata()

    newPixels = []
    for pixel in pixels:
        if pixel[0] == 245 and pixel[1] == 245 and pixel[2] == 245:
            newPixels.append((255, 255, 255, 0))
        else:
            newPixels.append((255, 255, 255, 255))
            #newPixels.append(pixel)

    img.putdata(newPixels)

    alpha = img.getchannel("A")
    bbox = alpha.getbbox()

    res = img.crop(bbox)
    res.save("processed.png", "png")
    print("saved!")

def rectangle(x, y, radius, rgb):
    image = Image.new("RGBA", (x, y), rgb)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((x, x, y, y), fill=rgb, radius=radius)
    return image

def drawstuff():

    """
    Let's make a white background, add some black bars for status stuff,
    And add a rectangular black box for the chemical
    Then we can jank-paste it all together.
    Maybe a loop!
    maybe not.
    """
 
    epd.width = 800
    epd.height = 480

    background = rectangle(800, 480, 0, "white")
    title_bar = rectangle(800, 40, 0, "black")

    background.paste(title_bar, (0, 0), title_bar)
    background.paste(title_bar, (0, 440), title_bar)



    with Image.open("processed.png") as chemical:
        width, height = chemical.size
        chemical = Image.open("processed.png")

    chemical_border = 50
    chemical_bg = rectangle(width + chemical_border, height + chemical_border, chemical_border, "black")

    chemical_bg_center = (int(chemical_border/2), int(chemical_border/2))
    chemical_bg.paste(chemical, chemical_bg_center, chemical)

    chemical_bg_y = int((epd.height - height - chemical_border)/2)
    background.paste(chemical_bg, (40, chemical_bg_y), chemical_bg)

    # background = rectangle(800, 480, 0, "#FFFFFF")

    # #background =  Image.open("bg.png")
    # with Image.open("processed.png") as chemical:
    #     width, height = chemical.size

    # chemical = Image.open("processed.png")


    # chemical_rect = rectangle(height, width, 50, "#000000")
    # chemical_rect.paste(chemical, (0,0), chemical_rect)

    # box_height = int((height/2))

    # chemicalbackground.paste(chemical_rect, (0,0), chemical_rect)
    # background.show()


    # # font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 40)
    # # d = ImageDraw.Draw(background)
    # # d.multiline_text((10, 10), "Hello\nWorld AAAAAA", font=font, fill=(125, 125, 125))



    epd.width = 800
    epd.height = 480
    epd.prepare()
    epd.clear()
    epd.display(background)
    epd.sleep()
    epd.close()



def main():
    print("Running main()   ")
    get_chem(1, 10000)
    image_processing("chem.png")
    drawstuff()

if __name__ == '__main__':
    main()
