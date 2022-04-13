import pubchempy as pcp
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageOps
import random
import numpy as np

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
            pcp.download('PNG', 'chem.png', n, overwrite=True, size="large")
            good_chem = True
            return formula, name
        except Exception as e:
            print(e)
            exit()
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
    res.save('processed.png', 'png')

get_chem(1, 10000)
image_processing("chem.png")






