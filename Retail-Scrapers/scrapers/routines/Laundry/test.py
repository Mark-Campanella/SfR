import pandas as pd

df = pd.read_csv("statics/product_link.csv")
df.drop_duplicates(keep="first", inplace=True)
df.to_csv("statics/product_link.csv", index=False)