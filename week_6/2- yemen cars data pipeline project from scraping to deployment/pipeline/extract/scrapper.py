from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import date
import re
from pathlib import Path


url = "https://ye.opensooq.com/ar/%D8%B3%D9%8A%D8%A7%D8%B1%D8%A7%D8%AA-%D9%88%D9%85%D8%B1%D9%83%D8%A8%D8%A7%D8%AA"
raw_dir = Path("data/raw")
raw_csv_path = raw_dir / "yemen_cars.csv"
raw_dir.mkdir(parents=True, exist_ok=True)
raw_cars = []

def get_response(url:str):
    # I include headers simulate a real browser request to avoid detiction
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "ar,en;q=0.9",
    }
    response = requests.get(url,headers=headers)
    response.raise_for_status()
    return response

def parse_page(url):
    soup= BeautifulSoup(get_response(url).text,"html.parser")
    return soup

def fetch_parent_element(soup,tag,**kwargs):
    soup= soup.find_all(tag,**kwargs)
    return soup

def extract_name(description = ""):
    try:
        name = description.split(',')[1].strip()
        return name
    except IndexError:
        return None

def extract_price(car):
    price_tag = car.find('div',class_="redColor bold font-18")
    price = price_tag.text.strip() if price_tag else None
    return price

def extract_model(description):
    model_text= description.split(',')[0]
    if model_text.isdigit():
        model =int(model_text)
    else :
        return None

    return model

def extract_post_date(car):
    date_tag = car.find('div',class_='darkGrayColor')
    if not date_tag:
        return None
    date_text = date_tag.text
    date_parts = date_text.split(" ")
    times= ["ساعة","ساعات","الأن","الان","دقائق","ثواني","قبل"]
    for i in times:
        if i in date_parts:
            return date.today()
    
    return date_parts[0]
    
def extract_status(car):
    try: 
        status =car.find_all('div',class_='flex alignItems gap-5')[0].text
        if status in ['مستعمل','جديد']:
            return status
        else:
            return None
    except IndexError: 
        return None

def extract_mileage(car):
    items = car.find_all('div', class_='flex alignItems gap-5')

    for item in items:
        text = item.get_text()

        if "كم" in text:
            numbers = re.findall(r"[\d,]+", text)
            values = [int(n.replace(",", "")) for n in numbers]

            if len(values) == 1:
                return values[0]

            if len(values) >= 2:
                return sum(values[:2]) / 2

    return None

def extract_location(car):
    location_tag = car.find('div', class_='flex alignItems font-13 bold')
    location_span = location_tag.find('span') if location_tag else None
    location = location_span.text.strip() if location_span else None    

    return location

def save_to_csv(raw_cars):
    df = pd.DataFrame(raw_cars)
    df.to_csv(raw_csv_path, index=False)
    print("\n*******************************************")
    print(f"                  Raw data saved successfully to {raw_csv_path}\n")

def scrape_yemen_cars():
    page = 1 
    is_page_avaliable= True
    while is_page_avaliable:

        soup = parse_page(f"{url}?page={page}")
        cars = fetch_parent_element(soup,'a',class_='sc-607e5a55-0') 

        for car in cars: 
            description = car.find('h2',class_='font-16 bold trimTwoLines').text.strip()
            model = extract_model(description)
            name = extract_name(description)
            posted_at = extract_post_date(car)
            image_url = car.find('img').get('src')
            price = extract_price(car)
            status = extract_status(car)
            mileage = extract_mileage(car)
            location = extract_location(car)
            
            raw_cars.append({
                "name":name,
                "description":description,
                "model":model,
                "posted_at":posted_at,
                "image_url":image_url,
                "price":price,
                "status":status,
                "mileage":mileage,
                "location":location,
                "country":"Yemen"
            }
            )
        
        save_to_csv(raw_cars)

        pagination_tag = soup.find('div',id='pagination')
        buttons = pagination_tag.find_all('a')

        for button in buttons: 
            nxt_btn = button.get('class')[-1]
            this_page= button.get('aria-label')
            if nxt_btn == "disabled" and this_page != "page 1":
               is_page_avaliable =False
               break
          
               
        print(f"*******page {page} scrapped successfully **********" )
