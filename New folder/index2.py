import json
from datetime import datetime, timedelta

# 1. Mock Dataset: Common Indian Grocery Items
# Shelf life is in hours under 'ideal' conditions (approx 20°C, 50% humidity)
pantry_data = [
    {"id": "item_001", "name": "Palak (Spinach)", "category": "leafy_greens", "ideal_shelf_life": 48, "purchase_time": "2026-02-18T10:00:00"},
    {"id": "item_002", "name": "Amul Milk", "category": "dairy", "ideal_shelf_life": 36, "purchase_time": "2026-02-18T08:00:00"},
    {"id": "item_003", "name": "Alphonso Mangoes", "category": "fruits", "ideal_shelf_life": 120, "purchase_time": "2026-02-17T12:00:00"},
    {"id": "item_004", "name": "Paneer", "category": "dairy", "ideal_shelf_life": 72, "purchase_time": "2026-02-18T14:00:00"},
    {"id": "item_005", "name": "Tomatoes", "category": "vegetables", "ideal_shelf_life": 168, "purchase_time": "2026-02-15T09:00:00"}
]

def calculate_ets(item, current_temp, current_humidity):
    # Base shelf life
    base_life = item['ideal_shelf_life']
    
    # Calculate decay coefficient (The 'Indian Weather' Factor)
    # Standard: 1.0. High Heat (>35C) or High Humidity (>80%): 1.5 acceleration.
    decay_coefficient = 1.0
    if current_temp > 35 or current_humidity > 80:
        decay_coefficient = 1.5
    
    # Adjusted shelf life based on environment
    adjusted_life_hrs = base_life / decay_coefficient
    
    # Calculate elapsed time since purchase
    purchase_dt = datetime.fromisoformat(item['purchase_time'])
    elapsed_hrs = (datetime.now() - purchase_dt).total_seconds() / 3600
    
    # Remaining time (ETS)
    ets_hrs = adjusted_life_hrs - elapsed_hrs
    return max(0, round(ets_hrs, 2))

def check_p2p_trigger(inventory, temp, humidity):
    broadcast_list = []
    
    for item in inventory:
        ets = calculate_ets(item, temp, humidity)
        
        # Output logic: Trigger broadcast if ETS < 24 hours
        if 0 < ets < 24:
            broadcast_payload = {
                "signal": "BIOMASS_AVAILABLE",
                "item_name": item['name'],
                "ets_remaining": f"{ets} hrs",
                "status": "URGENT",
                "p2p_mesh_id": f"node_{item['id']}"
            }
            broadcast_list.append(broadcast_payload)
            
    return json.dumps(broadcast_list, indent=2)

# --- SIMULATION ---
# Mumbai Monsoon Scenario: 32°C, 85% Humidity
mumbai_weather = {"temp": 32, "humidity": 85}
print(f"--- Mycelium P2P Broadcast Trigger (Weather: {mumbai_weather['temp']}°C, {mumbai_weather['humidity']}% Humidity) ---")
print(check_p2p_trigger(pantry_data, **mumbai_weather))