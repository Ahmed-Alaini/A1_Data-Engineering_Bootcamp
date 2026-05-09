import csv
import time
import random
import os
import uuid
from datetime import datetime

# Configuration
OUTPUT_DIR = "./data/income"
os.makedirs(OUTPUT_DIR, exist_ok=True)

products = ['PROD_001', 'PROD_002', 'PROD_003', 'PROD_004', 'PROD_005']
locations = ['New York', 'London', 'Tokyo', 'Berlin', 'Sydney', '']
statuses = ['COMPLETED', 'PENDING', 'FAILED', 'REFUNDED', 'UNKNOWN', '']
currencies = ['USD', 'EUR', 'GBP', 'JPY', '???', 'NONE', '']
payment_methods = ['CREDIT_CARD', 'PAYPAL', 'BANK_TRANSFER', 'CASH', '']

def generate_messy_reading():
    quantity = random.randint(1, 10)
    unit_price = round(random.uniform(5.0, 150.0), 2)
    total_amount = round(quantity * unit_price, 2)
    
    reading = {
        "transaction_id": str(uuid.uuid4()),
        "customer_id": f"CUST_{random.randint(1000, 9999)}",
        "product_id": random.choice(products),
        "quantity": quantity,
        "unit_price": unit_price,
        "total_amount": total_amount,
        "currency": random.choice(currencies),
        "payment_method": random.choice(payment_methods),
        "status": random.choice(statuses),
        "timestamp": datetime.now().isoformat(),
        "location": random.choice(locations)
    }
    
    # Introduce messy data (missing values, weird strings)
    if random.random() < 0.1: 
        reading["customer_id"] = '' # Missing customer
    if random.random() < 0.1:
        reading["quantity"] = 'N/A' # Messy quantity
        
    return reading

def write_to_csv():
    # please I need the current data and time in transaction file name

    filename = os.path.join(OUTPUT_DIR, f"transaction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    data = [generate_messy_reading() for _ in range(random.randint(1, 5))]
    
    # Introduce duplicates
    if random.random() < 0.2 and len(data) > 0:
        data.append(data[0]) 

    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["transaction_id", "customer_id", "product_id", "quantity", "unit_price", "total_amount", "currency", "payment_method", "status", "timestamp", "location"])
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Generated {filename}")

if __name__ == "__main__":
    print("Starting data simulation... Press Ctrl+C to stop.")
    try:
        while True:
            write_to_csv()
            time.sleep(2) # Writes files periodically
    except KeyboardInterrupt:
        print("Simulation stopped.")