import os 
import shutil
import pandas as pd 

csv_file = 'data/raw/CSV/raw_data.csv'
if not os.path.exists(csv_file):
    csv_file = 'data/raw/CSV/books.csv'

df = pd.read_csv(csv_file)
df.columns = df.columns.str.strip().str.lower()
df = df.rename(
    columns={
        'name:': 'name',
        'price:': 'price',
        'rating:': 'rating',
        'file_path:': 'image'
    }
)

mapping ={
    "Zero":0,
    "One":1,
    "Two":2,
    "Three":3,
    "Four":4,
    "Five":5
}

df['rating'] = df['rating'].replace(mapping)
df['rating'] = pd.to_numeric(df['rating'],errors='coerce')
df = df.dropna(subset=['rating'])
df['rating'] = df['rating'].astype(int)

for i in sorted(df['rating'].unique()):
    os.makedirs(f"data/raw/images/{i}_star",exist_ok=True)
    os.makedirs(f"data/raw/CSV/{i}_star",exist_ok=True)


for _,row in df.iterrows():
    src= row['image']
    rating= int(row['rating'])
    dist =f"data/raw/images/{rating}_star/{os.path.basename(src)}"

    if os.path.exists(src) and os.path.abspath(src) != os.path.abspath(dist):
        shutil.move(src,dist)

    if os.path.exists(dist):
        df.at[_, 'image'] = dist


for rating in sorted(df['rating'].unique()):
    rating_df = df[df['rating'] == rating]
    rating_df.to_csv(f"data/raw/CSV/{rating}_star/raw_data.csv",index=False)


df.to_csv('data/raw/CSV/raw_data.csv',index=False)
