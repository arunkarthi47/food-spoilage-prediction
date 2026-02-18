import json
from datetime import datetime, timedelta

# Mock dataset of 5 common Indian grocery items
ITEMS = [
    {"name": "Spinach", "category": "leafy greens", "base_ets": 48, "decay_coeff": 1.0},
    {"name": "Potato", "category": "tubers", "base_ets": 144, "decay_coeff": 1.0},
    {"name": "Milk", "category": "dairy", "base_ets": 72, "decay_coeff": 1.0},
    {"name": "Coriander", "category": "leafy greens", "base_ets": 36, "decay_coeff": 1.0},
    {"name": "Yogurt", "category": "dairy", "base_ets": 96, "decay_coeff": 1.0},
]

# Optimal storage conditions
OPTIMAL_TEMP = {"leafy greens": 5, "tubers": 10, "dairy": 4}  # °C
OPTIMAL_HUMIDITY = 70  # %

def predict_ets(purchase_date_str, item_name, current_temp, current_humidity):

    # Parse purchase date
    purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%d %H:%M")

    # Find item data
    item = next((i for i in ITEMS if i["name"].lower() == item_name.lower()), None)
    if not item:
        raise ValueError(f"Item '{item_name}' not found in dataset.")

    category = item["category"]
    base_ets = item["base_ets"]
    decay_coeff = item["decay_coeff"]

    # Calculate weather delta
    temp_delta = current_temp - OPTIMAL_TEMP[category]
    humidity_delta = current_humidity - OPTIMAL_HUMIDITY

    # Accelerate decay if weather is harsh
    if current_humidity > 80 or current_temp > 35:
        decay_coeff *= 1.5

    # Adjust ETS
    temp_factor = max(0, 1 - 0.05 * max(0, temp_delta))
    humidity_factor = max(0, 1 - 0.01 * max(0, humidity_delta))

    adjusted_ets_hours = base_ets * decay_coeff * temp_factor * humidity_factor

    # Calculate hours passed since purchase
    now = datetime.now()
    hours_since_purchase = (now - purchase_date).total_seconds() / 3600

    # Calculate remaining ETS
    remaining_ets = adjusted_ets_hours - hours_since_purchase

    # Check if trigger is needed
    trigger = None
    if remaining_ets < 24:
        trigger = {
            "item": item_name,
            "category": category,
            "remaining_ets_hours": round(remaining_ets, 2),
            "trigger": "P2_P_BROADCAST_INITIATE"
        }

    return remaining_ets, trigger


# Example usage
if __name__ == "__main__":
    purchase_date = "2026-02-17 08:00"  # recent date
    current_temp = 36
    current_humidity = 85
    item_name = "Spinach"

    remaining_ets, trigger_json = predict_ets(
        purchase_date, item_name, current_temp, current_humidity
    )

    print(f"Remaining ETS (hours): {remaining_ets:.2f}")

    if trigger_json:
        print("Trigger JSON:")
        print(json.dumps(trigger_json, indent=2))
