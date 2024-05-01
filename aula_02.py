import pandas as pd

base = pd.read_csv("https://www.football-data.co.uk/mmz4281/2324/E0.csv")

base.to_csv("Base.csv",index=False)

