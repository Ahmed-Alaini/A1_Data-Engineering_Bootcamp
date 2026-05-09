import os, csv, json, time, random, uuid
from datetime import datetime, timedelta
from pathlib import Path

WATCH_DIR = os.getenv("WATCH_DIR", "E:/DE_A1/Data Engineering Bootcamp/spark-sql-and-pyspark-using-python3/lab_data/data/incoming")
Path(WATCH_DIR).mkdir(parents=True, exist_ok=True)

FIELDS = [
    "transaction_id", "customer_id", "product_id", "quantity", "unit_price",
    "total_amount", "currency", "payment_method", "status", "timestamp", "location"
]

def maybe(value, chance=0.1):
    return "" if random.random() < chance else value

def transaction_id():
    if random.random() < 0.05:
        return f"{random.randint(1000, 1050)}"
    return f"{uuid.uuid4().hex[:8].upper()}"

def timestamp():
    date = datetime.now() - timedelta(seconds=random.randint(0, 3600))
    return random.choice([
        date.strftime("%Y-%m-%d %H:%M:%S"),
        date.strftime("%m/%d/%Y %I:%M:%S %p"),
        date.isoformat()
    ])

def make_record():
    qty = random.choice([random.randint(1, 50), "N/A"])
    price = maybe(round(random.uniform(1, 999.99), 2), 0.08)

    total = 0
    if isinstance(qty, int) and price != "":
        total = round(qty * price, 2)

    return {
        "transaction_id": transaction_id(),
        "customer_id": maybe(f"CUST-{random.randint(1000, 9999)}"),
        "product_id": f"PROD-{random.randint(100, 999)}",
        "quantity": qty,
        "unit_price": price,
        "total_amount": total,
        "currency": maybe(random.choice(["USD", "EUR", "GBP", "JPY", "???", "NONE", ""])),
        "payment_method": maybe(random.choice(["CREDIT_CARD", "DEBIT_CARD", "CASH", "PAYPAL"])),
        "status": random.choice(["COMPLETED", "PENDING", "FAILED", "REFUNDED", ""]),
        "timestamp": timestamp(),
        "location": maybe(random.choice(["New York", "London", "Tokyo", "Dubai"]))
    }

def save_file(records, path, file_type):
    with open(path, "w", newline="", encoding="utf-8") as file:
        if file_type == "csv":
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(records)

        elif file_type == "json":
            for record in records:
                file.write(json.dumps(record) + "\n")

        else:
            file.write("|".join(FIELDS) + "\n")
            for record in records:
                file.write("|".join(str(record[field]) for field in FIELDS) + "\n")

def main():
    while True:
        file_type = random.choice(["csv", "json", "txt"])
        records = [make_record() for _ in range(random.randint(50, 200))]

        name = f"Transaction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_type}"
        path = os.path.join(WATCH_DIR, name)

        save_file(records, path, file_type)

        print(f"Created {name} with {len(records)} records")
        time.sleep(random.randint(2, 5))

if __name__ == "__main__":
    main()


