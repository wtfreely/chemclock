import pubchempy as pcp
import pandas as pd
import random
import time
import warnings
from PIL import Image

warnings.simplefilter(action='ignore', category=FutureWarning)

'''
This is the get_chem function
It polls pubchem for data and outputs it for us
'''

def get_chem(n):
    n = n
    good_chem = False
    while good_chem == False:
        try:
            c = pcp.Compound.from_cid(n)
            # print(c.synonyms)
            id = n
            formula = c.molecular_formula
            name = c.iupac_name
            synonyms = c.synonyms
            weight = c.molecular_weight
            complexity = c.complexity
            img_loc = r"img/"
            filetype = ".png"
            filename = str(img_loc) + str(id) + str(filetype) 
            pcp.download('PNG', filename, id, overwrite=True, size=400)
            good_chem = True
            return id, formula, name, synonyms, weight, complexity
        except Exception as e:
            print(e)
            good_chem = False
            print("Error.  Possible bad chemical or lack of internet?")

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
    res.save(image, "png")
    print("Saved processed image.")

def main():

    '''
    First, let's establish if there is a dataframe as df.ftr,
    If not, we make one with the requisite columns
    So we can dump get_chem as a new row
    '''

    df_feather_loc = r"df.ftr"

    try:
        df = pd.read_feather(df_feather_loc)
        print("Existing dataframe detected, using it!")
    except Exception as e:
        print(e)
        df = pd.DataFrame(columns = ['id','formula', 'name', 'synonyms', 'weight', 'complexity', 'img']).set_index("id")
        print("No dataframe detected, making one!")

    i = 1
    while i < 365:
        chem_data = get_chem(i)
        new_row = {"id":chem_data[0], "formula":chem_data[1], "name":chem_data[2], "synonyms":chem_data[3], "weight":chem_data[4], "complexity":chem_data[5]}
        print(new_row)
        file_loc = r"img/"
        file_type = ".png"
        filename = file_loc + str(i) + file_type
        image_processing(filename)
        df = df.append(new_row, ignore_index=True)
        i += 1
        time.sleep(3)

    df.to_feather(df_feather_loc)

if __name__ == '__main__':
    main()