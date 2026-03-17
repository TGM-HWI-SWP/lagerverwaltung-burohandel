"""Überprüfe Datenbankinhalt"""
import sqlite3
import os

db_path = "warehouse.db"

if not os.path.exists(db_path):
    print(f"Fehler: Datenbank existiert nicht: {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabellen anzeigen
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tabellen in der Datenbank:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Produktanzahl
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    print(f"\nProdukte in der Datenbank: {count}")
    
    if count > 0:
        # Erste 3 Produkte anzeigen
        cursor.execute("SELECT id, name, warehouse_qty, shop_qty FROM products LIMIT 3")
        print("\n  Beispiele:")
        for row in cursor.fetchall():
            print(f"    - {row[1]} (ID: {row[0]}) - Lager: {row[2]}, Shop: {row[3]}")
    else:
        print("  Fehler: KEINE PRODUKTE IN DER DATENBANK!")
    
    # Bewegungen anzeigen
    cursor.execute("SELECT COUNT(*) FROM movements")
    movement_count = cursor.fetchone()[0]
    print(f"\nBewegungen in der Datenbank: {movement_count}")
    
    conn.close()
    
except Exception as e:
    print(f"Fehler beim Überprüfen der Datenbank: {e}")
