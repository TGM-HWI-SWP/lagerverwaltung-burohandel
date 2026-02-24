"""Database Initialization Script"""

import json
from pathlib import Path

from src.adapters.repository import SQLiteRepository
from src.domain.product import Product


def init_database_with_sample_data(db_path: str = "warehouse.db") -> None:
    """
    Datenbank mit sample_data.json initialisieren

    Args:
        db_path: Pfad zur Datenbank
    """
    # Sample Daten laden
    sample_data_path = Path(__file__).parent / "src" / "adapters" / "sample_data.json"

    if not sample_data_path.exists():
        print(f"Fehler: sample_data.json nicht gefunden unter {sample_data_path}")
        return

    with open(sample_data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Repository initialisieren
    repo = SQLiteRepository(db_path=db_path)

    # Produkte laden und speichern
    printed_products = False
    for product_data in data.get("warehouse", {}).get("products", []):
        try:
            product = Product(
                id=product_data.get("id"),
                name=product_data.get("name"),
                description=product_data.get("description", ""),
                price=float(product_data.get("price", 0)),
                warehouse_qty=int(product_data.get("quantity", 0)),
                shop_qty=0,  # Anfangs kein Bestand im Shop
                sku=product_data.get("sku", ""),
                category=product_data.get("category", ""),
                notes=product_data.get("notes", ""),
            )
            repo.save_product(product)

            if not printed_products:
                print(f"Produkt '{product.name}' in Datenbank geladen")
                printed_products = True

        except Exception as e:
            print(f"Fehler beim Laden von Produkt: {e}")

    print(f"Datenbank erfolgreich mit {len(data.get('warehouse', {}).get('products', []))} Produkten initialisiert!")


if __name__ == "__main__":
    init_database_with_sample_data()
