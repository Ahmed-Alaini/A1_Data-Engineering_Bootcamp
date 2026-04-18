import os 
import pandas as pd 

path = "data/processed/"
os.makedirs(path,exist_ok=True)

csv_files = []
csv_folder = "data/raw/CSV"

if os.path.exists(csv_folder):
    for folder in os.listdir(csv_folder):
        folder_path = os.path.join(csv_folder,folder)
        file_path = os.path.join(folder_path,'raw_data.csv')

        if os.path.isdir(folder_path) and os.path.exists(file_path):
            csv_files.append(file_path)

if csv_files:
    dataframes = [pd.read_csv(file) for file in csv_files]
    df = pd.concat(dataframes,ignore_index=True)
else:
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

df= df.drop_duplicates()

# to keep only the price number and convert it as float
df['price']= df['price'].astype(str).str.replace(r'[^\d.]','',regex= True)
df['price']= pd.to_numeric(df['price'],errors='coerce')
df['price'] = df['price'].fillna(df['price'].mean())

mapping ={
    "Zero":0,
    "One":1,
    "Two":2,
    "Three":3,
    "Four":4,
    "Five":5
}

df['rating']= df['rating'].replace(mapping)
df['rating']= pd.to_numeric(df['rating'],errors='coerce')
df= df.dropna(subset=['rating'])
df['rating']= df['rating'].astype(int)

df.to_csv(path+'cleaned_books.csv',index=False)

