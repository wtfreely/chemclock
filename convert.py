import pandas as pd


df = pd.read_feather(r"df.ftr")
df.to_pickle("df.pkl")

pd.read