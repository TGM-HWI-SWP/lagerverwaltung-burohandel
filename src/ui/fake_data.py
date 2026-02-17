# Fake-Daten, bis DB/Services vom Kollegen kommen

PRODUCTS = [
    {"id": 1, "name": "Kugelschreiber", "shop_qty": 10, "warehouse_qty": 50},
    {"id": 2, "name": "Bleistift", "shop_qty": 8, "warehouse_qty": 40},
    {"id": 3, "name": "Notizblock A5", "shop_qty": 5, "warehouse_qty": 25},
    {"id": 4, "name": "Druckerpapier A4 (500)", "shop_qty": 3, "warehouse_qty": 30},
    {"id": 5, "name": "Ordner", "shop_qty": 6, "warehouse_qty": 20},
]

def list_products():
    # liefert zusätzlich total
    view = []
    for p in PRODUCTS:
        view.append({
            "id": p["id"],
            "name": p["name"],
            "shop_qty": p["shop_qty"],
            "warehouse_qty": p["warehouse_qty"],
            "available_total": p["shop_qty"] + p["warehouse_qty"],
        })
    return view
