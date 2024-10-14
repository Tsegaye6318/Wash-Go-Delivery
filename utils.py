def calculate_price_by_weight(weight, is_first_time_customer=False):
    base_price = 0.00
    price_per_kg = 4.19  # $1.90 per pound is approximately $4.19 per kg
    total_price = base_price + (weight * price_per_kg)
    minimum_charge = 38.00  # 20-pound minimum
    total_price = max(total_price, minimum_charge)
    
    if is_first_time_customer:
        total_price *= 0.8  # Apply 20% discount for first-time customers
    
    return total_price

def calculate_price_for_special_items(blankets=0, pillows=0):
    blanket_price = 15.00
    pillow_price = 7.00
    return (blankets * blanket_price) + (pillows * pillow_price)

def calculate_total_price(weight, blankets=0, pillows=0, is_first_time_customer=False):
    weight_price = calculate_price_by_weight(weight, is_first_time_customer)
    special_items_price = calculate_price_for_special_items(blankets, pillows)
    return weight_price + special_items_price
