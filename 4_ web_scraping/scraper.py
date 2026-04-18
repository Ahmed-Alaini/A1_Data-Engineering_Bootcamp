import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import os
import pandas as pd 

BaseUrl= "https://books.toscrape.com/catalogue/page-1.html"

img_path= "data/raw/images/"
csv_path= "data/raw/CSV/"

os.makedirs(img_path,exist_ok=True)
os.makedirs(csv_path,exist_ok=True)

Raw_Books = []

def get_response(url:str):
    response = requests.get(url)
    response.raise_for_status()
    return response

def parse_page(url):
    soup= BeautifulSoup(get_response(url).text,"html.parser")
    return soup


def get_elements(soup,tag,**kwargs):
    return soup.find_all(tag,**kwargs)

def get_image_content(article):
    img_src= article.find('img').get('src')
    img_url =urljoin(BaseUrl,img_src)
    img_content= get_response(img_url).content
    
    return img_content

def clean_name(name):
    # make the name samller than 50 char
    name= name[:50]

    name= name.lower()
    # remove whitespace
    name= name.replace(" ","_")
    # remove spcial characters
    name= re.sub(r'[<>:"/\\|?*]','',name)

    return name

def save_images_to_folder(img_content,name):
        name= clean_name(name)
        file_path = img_path+name+".png"
        with open(file_path,"wb") as img_file:
            img_file.write(img_content)
        print(name + " Saved to "+img_path)
        return file_path

def books_info(articles):
    for article in articles:
        name = article.find('h3').a.get('title')
        price = article.find('p',class_='price_color').text
        rating = article.find('p',class_='star-rating').get('class')[1]
        # to get the image content as binary content form the URL 
        img_content = get_image_content(article)
        # to save the images to the raw_imagaes folder
        image_path = save_images_to_folder(img_content,name)

        Raw_Books.append(
            {
                "name":name,
                "price":price,
                "rating":rating,
                "image":image_path
            }
        )

def save_raw_data(Raw_Books):
    df = pd.DataFrame(Raw_Books)
    print(df.head())
    df.to_csv(csv_path+"raw_data.csv",index=False)
    print("\n*******************************************")
    print("                  Row Data Saved Successfully to "+csv_path+"\n")

def main():
    URL =BaseUrl
    current_page=1
    while URL and current_page <= 3 :
        soup = parse_page(URL)
        articles = get_elements(soup,'article',class_='product_pod')
        
        
        print(f"\n*****************current_page is {current_page} **********************\n")
        
        # take the article to extract books info and sotre each book in Raw_Books
        books_info(articles)
        # to save raw books to a folder 
        save_raw_data(Raw_Books)

        # to check the the next button is exist or not 
        nxt_btn = soup.find('li', class_='next')
        
        if nxt_btn:
            current_page+=1
            URL= f"https://books.toscrape.com/catalogue/page-{current_page}.html"
        else :
            URL=None



# if __name__ == "__main__":
main()
