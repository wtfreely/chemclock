"""

Thanks to Rob Weber for making omni-epd.
It sure made dealing with this a lot easier.

"""

import os
import sys
import random
import datetime
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
today = datetime.date.today()

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
            print(c.synonyms)
            formula = c.molecular_formula
            name = c.iupac_name
            synonyms = c.synonyms
            weight = c.molecular_weight
            complexity = c.complexity
            pcp.download('PNG', 'chem.png', n, overwrite=True, size=400)
            good_chem = True
            return formula, name, synonyms, weight, complexity
        except Exception as e:
            print(e)
            good_chem = False
            print("Error.  Possible bad chemical or lack of internet?")

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
    print("Saved processed image.")

def rectangle(x, y, radius, rgb):
    image = Image.new("RGBA", (x, y), rgb)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((0, x, 0, y), fill=rgb, outline=None, width=1, radius=radius)
    return image

def drawstuff(name):

    """
    Let's make a white background, add some black bars for status stuff,
    And add a rectangular black box for the chemical
    Then we can jank-paste it all together.
    Maybe a loop!
    Maybe not.
    """
 
    ### Defining our canvas size since we use these values for a lot of math.

    epd.width = 800
    epd.height = 480

    ### Molecules look a lot nicer with subscript, don't you think?

    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

    molecule_formula = name[0].translate(SUB)
    molecule_name = name[1]
    molecule_synonyms = name[2]
    molecule_weight = name[3]
    molecule_complexity = name[4]

    ### Let's make out background just a nice, white rectangle
    ### And define our fonts :)

    background = rectangle(800, 480, 0, "white")
    header = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf", 28)
    paragraph = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", 22)

    ### Our title bar can go at the top
    ### And get a nice white title on it :)

    title_bar = rectangle(800, 40, 0, "black")
    d = ImageDraw.Draw(title_bar)
    d.multiline_text((10, 3), str("voilà chemclock.py"), font=header, fill=(255, 255, 255))

    ### And a status bar can have the date

    status_bar = rectangle(800, 40, 0, "black")
    d = ImageDraw.Draw(status_bar)
    d.multiline_text((10, 3), today.strftime("molécule du jour pour le %d de %B, %Y"), font=header, fill=(255, 255, 255))

    ### Add 'em to the background!
    
    background.paste(title_bar, (0, 0), title_bar)
    background.paste(status_bar, (0, 440), title_bar)

    ### Now let's draw the chemical structure

    with Image.open("processed.png") as chemical:
        width, height = chemical.size
        chemical = Image.open("processed.png")

    chemical_border = 50
    chemical_bg = rectangle(width + chemical_border, height + chemical_border, chemical_border, "black")

    chemical_bg_center = (int(chemical_border/2), int(chemical_border/2))
    chemical_bg.paste(chemical, chemical_bg_center, chemical)

    chemical_bg_y = int((epd.height - height - chemical_border)/2)
    background.paste(chemical_bg, (40, chemical_bg_y), chemical_bg)

    ### oKAY now let's draw some actual text for the thingy okay :)

    d = ImageDraw.Draw(background)
    d.multiline_text((width + chemical_border + 75, 110), str(f"formule moléculaire: %su" % (molecule_formula)), font=paragraph, fill=(000, 000, 00))

    if len(molecule_synonyms) == 0:
        d = ImageDraw.Draw(background)
        d.multiline_text((width + chemical_border + 75, 190), str(f"pas des synonymes connus."), font=paragraph, fill=(000, 000, 00))
    elif len(molecule_synonyms) > 0:
        d = ImageDraw.Draw(background)
        d.multiline_text((width + chemical_border + 75, 190), str(f"synonyme connu: %s" % (molecule_synonyms[0])), font=paragraph, fill=(000, 000, 00))


    d.multiline_text((width + chemical_border + 75, 270), str(f"masse moléculaire: %su" % (molecule_weight)), font=paragraph, fill=(000, 000, 00))
    d.multiline_text((width + chemical_border + 75, 350), str(f"évaluation de la complexité: %s" % (molecule_complexity)), font=paragraph, fill=(000, 000, 00))

    epd.prepare()
    epd.clear()
    epd.display(background)
    epd.sleep()
    epd.close()



def main():
    print("Running main()  ")
    molecule = get_chem(1, 10000)
    image_processing("chem.png")
    drawstuff(molecule)

if __name__ == '__main__':
    main()