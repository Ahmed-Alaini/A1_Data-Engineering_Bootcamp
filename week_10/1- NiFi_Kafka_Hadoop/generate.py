import csv
import os
import random
import time
from datetime import datetime, timedelta

OUTPUT_DIR = "./stream_data"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def random_timestamp():
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%m-%d-%Y %H:%M",
    ]
    dt = datetime.now() - timedelta(seconds=random.randint(0, 10000))
    return dt.strftime(random.choice(formats))


def corrupt_row():
    return ["CORRUPT", "", "NOT_A_NUMBER", "9999", "NAN", "UNKNOWN", "NOT_A_DATE"]


def generate_record():
    meter_id = f"MTR{random.randint(1000, 1010)}"
    building_id = f"BLD{random.randint(200, 210)}"
    power = round(random.uniform(0.5, 20.0), 2)
    voltage = random.choice([220, 230, 110, None])
    current = round(random.uniform(1, 50), 2)
    status = random.choice(["ACTIVE", "INACTIVE", "FAULT"])
    timestamp = random_timestamp()

    # inject anomalies
    if random.random() < 0.1:
        return corrupt_row()

    if random.random() < 0.1:
        building_id = ""

    if random.random() < 0.1:
        power = -abs(power)

    if random.random() < 0.1:
        timestamp = "INVALID_DATE"
    if random.random() < 0.05:
        power = "NAN"  # String instead of number
    if random.random() < 0.05:
        current = "INF"  # Invalid numeric string
    if random.random() < 0.05:
        voltage = 9999  # Unrealistic value

    return [meter_id, building_id, power, voltage, current, status, timestamp]


def get_filename():
    # filename based on current date & time
    return datetime.now().strftime("meter_data_%Y-%m-%d_%H-%M-%S.csv")


def write_file():
    filename = os.path.join(OUTPUT_DIR, get_filename())

    header = ["meter_id", "building_id", "power_kw", "voltage", "current", "status", "timestamp"]

    records = []

    for _ in range(20):
        record = generate_record()
        records.append(record)

        # duplicates simulation
        if random.random() < 0.1:
            records.append(record.copy())
            
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(records)

    print(f"[+] Generated: {filename} ({len(records)} records)")


def stream_generator():
    while True:
        write_file()
        time.sleep(3)


if __name__ == "__main__":
    stream_generator()
