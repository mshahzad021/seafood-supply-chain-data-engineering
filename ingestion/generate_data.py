
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

products = [
    (101, "Atlantic Salmon", 12.50),
    (102, "Atlantic Cod", 10.00),
    (103, "Snow Crab", 18.75),
    (104, "Lobster", 24.00),
    (105, "Sea Scallops", 21.50),
    (106, "Rainbow Trout", 9.25),
    (107, "Halibut", 16.00),
    (108, "Blue Mussels", 7.50),
]

locations = ["Saint John", "Moncton", "Halifax", "Fredericton", "St. Andrews"]
customers = list(range(1001, 1501))
statuses = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]

start_date = date(2025, 1, 1)
end_date = date(2026, 11, 1)
date_range = (end_date - start_date).days

def random_date():
    return start_date + timedelta(days=random.randint(0, date_range))

# 1. Generate Orders
orders = []

for order_id in range(1, 10001):
    product_id, product_name, base_price = random.choice(products)
    quantity = random.randint(5, 200)
    order_date = random_date()

    orders.append({
        "order_id": order_id,
        "customer_id": random.choice(customers),
        "order_date": order_date,
        "product_id": product_id,
        "quantity": quantity,
        "unit_price": round(base_price * random.uniform(0.9, 1.15), 2),
        "order_status": random.choice(statuses),
        "source_location": random.choice(locations),
    })

with open(RAW_DIR / "orders.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=orders[0].keys())
    writer.writeheader()
    writer.writerows(orders)

# 2. Generate Inventory
inventory = []

for inventory_id in range(1, 5001):
    product_id, product_name, base_price = random.choice(products)

    inventory.append({
        "inventory_id": inventory_id,
        "product_id": product_id,
        "product_name": product_name,
        "location_id": random.choice(locations),
        "quantity_on_hand": random.randint(0, 2000),
        "reorder_level": random.randint(100, 500),
        "unit_cost": round(base_price * random.uniform(0.5, 0.8), 2),
    })

with open(RAW_DIR / "inventory.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=inventory[0].keys())
    writer.writeheader()
    writer.writerows(inventory)

# 3. Generate Shipments for 8,000 orders
shipments = []

for shipment_id in range(1, 8001):
    order = orders[shipment_id - 1]
    shipped_date = order["order_date"] + timedelta(days=random.randint(0, 3))
    expected_date = shipped_date + timedelta(days=random.randint(2, 7))

    shipment_status = random.choice(
        ["In Transit", "Delivered", "Delayed"]
    )

    actual_date = (
        expected_date + timedelta(days=random.randint(-1, 4))
        if shipment_status == "Delivered"
        else ""
    )

    shipments.append({
        "shipment_id": shipment_id,
        "order_id": order["order_id"],
        "origin_location": order["source_location"],
        "destination_location": random.choice(locations),
        "shipped_date": shipped_date,
        "expected_delivery_date": expected_date,
        "actual_delivery_date": actual_date,
        "shipment_status": shipment_status,
        "carrier": random.choice(["Maersk", "FedEx", "DHL", "Local Carrier"]),
        "tracking_number": f"SEA{shipment_id:08d}",
    })

with open(RAW_DIR / "shipments.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=shipments[0].keys())
    writer.writeheader()
    writer.writerows(shipments)

print("Synthetic data generation completed!")
print(f"Orders: {len(orders)}")
print(f"Inventory: {len(inventory)}")
print(f"Shipments: {len(shipments)}")
print(f"Output directory: {RAW_DIR}")
