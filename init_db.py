"""Datenbank initialisieren und mit Sample-Daten füllen"""

import json
import os
from datetime import datetime
from pathlib import Path

from src.adapters.repository import SQLiteRepository
from src.domain.product import Product


def load_sample_data():
    """Sample-Daten aus JSON laden"""
    sample_file = Path(__file__).parent / "src" / "adapters" / "sample_data.json"
    
    if not sample_file.exists():
        print(f"❌ Sample-Datei nicht gefunden: {sample_file}")
        return []
    
    with open(sample_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    products = []
    for product_data in data.get("warehouse", {}).get("products", []):
        # Timestamps konvertieren
        created_at = product_data.get("created_at")
        updated_at = product_data.get("updated_at")
        
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        product = Product(
            id=product_data["id"],
            name=product_data["name"],
            description=product_data["description"],
            price=product_data["price"],
            warehouse_qty=product_data.get("quantity", 0),
            shop_qty=0,  # Anfangs keine Produkte im Shop
            sku=product_data.get("sku", ""),
            category=product_data.get("category", ""),
            notes=product_data.get("notes", ""),
            created_at=created_at,
            updated_at=updated_at,
        )
        products.append(product)
    
    return products


def init_database(db_path: str = "warehouse.db"):
    """Datenbank initialisieren und mit Sample-Daten füllen"""
    # Alte Datenbank löschen, wenn vorhanden
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️  Alte Datenbank gelöscht: {db_path}")
    
    print(f"📦 Initialisiere neue Datenbank: {db_path}")
    
    # Repository erstellen (initialisiert Tabellen mit neuem Schema)
    repository = SQLiteRepository(db_path=db_path)
    
    # Sample-Daten laden
    products = load_sample_data()
    
    if not products:
        print("❌ Keine Produkte zum Laden gefunden")
        return False
    
    # Produkte in Datenbank speichern
    for product in products:
        repository.save_product(product)
        print(f"✅ {product.name} ({product.id})")
    
    print(f"\n✨ Datenbank erfolgreich initialisiert mit {len(products)} Produkten!")
    return True


if __name__ == "__main__":
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else "warehouse.db"
    init_database(db_path)
