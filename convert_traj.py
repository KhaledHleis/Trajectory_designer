import pandas as pd

#import trajectory
filename = "save/lonlat_traj_acBous_150deg_mars26.csv"
df= pd.read_csv(filename)

cols = ['longitude','latitude']
df = df.drop(columns="heading")
df = df.drop_duplicates()
import matplotlib.pyplot as plt
plt.plot(df["longitude"])
plt.show()

df[cols].to_csv(f'convert/lonlat_traj_acBous_150deg_mars26.txt', index=False,header=False) 
