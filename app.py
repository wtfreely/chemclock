"""

Thanks to Rob Weber for making omni-epd.
It sure made dealing with this a lot easier.

"""

import os
import sys
import datetime
import locale
import random
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
today = datetime.date.today()
from omni_epd import displayfactory, EPDNotFoundError
from PIL import Image, ImageDraw, ImageFont
import pandas as pd

"""

Be sure to include omni-epd.ini in local folder,
as it is critical for adjusting rotation and other post-processing.

"""

try:
    epd = displayfactory.load_display_driver("waveshare_epd.epd7in5_V2")
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

"""
Let's start by grabbing a random molecule from the dataframe
Let's get the length of the dataframe (number of rows) and query a random row between 0 and that
"""

def get_molecule():
    df_pickle_loc = r"df.pkl"
    df = pd.read_pickle(df_pickle_loc)
    max = len(df)
    index = random.randint(0, max)
    molecule = df.iloc[index]
    return molecule

def rectangle(x, y, radius, rgb):
    image = Image.new("RGBA", (x, y), rgb)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((0, x, 0, y), fill=rgb, outline=None, width=1, radius=radius)
    return image

def drawstuff(molecule):

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

    molecule_formula = molecule["formula"].translate(SUB)
    molecule_name = molecule["name"]
    molecule_synonyms = molecule["synonyms"]
    molecule_weight = molecule["weight"]
    molecule_complexity = molecule["complexity"]
    molecule_img = r"img/" + str(round(molecule["id"])) + r".png"

    ### Let's make out background just a nice, white rectangle
    ### And define our fonts :)

    background = rectangle(800, 480, 0, "white")
    header = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf", 28)
    paragraph = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", 22)

    ### Our title bar can go at the top
    ### And get a nice white title on it :)

    title_bar = rectangle(800, 40, 0, "black")
    d = ImageDraw.Draw(title_bar)
    d.multiline_text((10, 3), str("chemiCalendrier"), font=header, fill=(255, 255, 255))

    ### And a status bar can have the date

    status_bar = rectangle(800, 40, 0, "black")
    d = ImageDraw.Draw(status_bar)
    d.multiline_text((10, 3), today.strftime("date: %d de %B, %Y"), font=header, fill=(255, 255, 255))

    ### Add 'em to the background!
    
    background.paste(title_bar, (0, 0), title_bar)
    background.paste(status_bar, (0, 440), title_bar)

    ### Now let's draw the chemical structure

    with Image.open(molecule_img) as chemical:
        width, height = chemical.size
        chemical = Image.open(molecule_img)

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
    molecule = get_molecule()
    type(molecule)
    print(molecule)
    print(type(molecule))
    drawstuff(molecule)

if __name__ == '__main__':
    main()