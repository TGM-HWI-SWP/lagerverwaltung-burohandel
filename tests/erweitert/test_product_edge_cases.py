"""Erweiterte Tests - Randfälle und Fehlerfälle für Product"""

import pytest
from datetime import datetime
from src.domain.product import Product


class TestProductEdgeCases:
    """Randfälle für Product-Klasse
    
    Diese Test-Klasse prüft, wie die Product-Klasse mit extremen,
    aber gültigen Situationen umgeht (z.B. kostenlose Artikel,
    riesige Mengen, sehr lange Namen).
    """

    def test_product_with_zero_price(self):
        """Test: Produkt mit Preis = 0 (kostenlos) sollte erlaubt sein
        
        Wir prüfen, dass kostenlose Artikel richtig funktionieren.
        Der Gesamtwert sollte auch 0 sein, auch wenn Bestand vorhanden ist.
        """
        # Kostenloses Produkt mit 100 Stück erstellen
        product = Product(
            id="FREE001",
            name="Kostenloses Produkt",
            description="Gratis Artikel",
            price=0.0,  # Preis = GRATIS!
            warehouse_qty=100,
        )
        # Prüfe: Preis ist wirklich 0
        assert product.price == 0.0
        # Prüfe: Gesamtwert ist auch 0 (100 * 0 = 0)
        assert product.get_total_value() == 0.0

    def test_product_with_very_large_price(self):
        """Test: Produkt mit sehr großem Preis"""
        large_price = 999999.99
        product = Product(
            id="EXPENSIVE",
            name="Teures Produkt",
            description="Sehr wertvoll",
            price=large_price,
            warehouse_qty=1,
        )
        assert product.price == large_price
        assert product.get_total_value() == large_price

    def test_product_with_zero_stock(self):
        """Test: Produkt mit 0 Bestand"""
        product = Product(
            id="P001",
            name="Ausverkauftes Produkt",
            description="Keine Einheiten",
            price=10.0,
            warehouse_qty=0,
            shop_qty=0,
        )
        assert product.get_total_qty() == 0
        assert product.get_total_value() == 0.0
        assert not product.is_low_stock()

    def test_product_with_large_stock(self):
        """Test: Produkt mit sehr großem Bestand"""
        large_qty = 1000000
        product = Product(
            id="P002",
            name="Großes Lager",
            description="Viel Bestand",
            price=1.0,
            warehouse_qty=large_qty,
        )
        assert product.get_total_qty() == large_qty
        assert product.get_total_value() == float(large_qty)

    def test_product_min_stock_level_zero(self):
        """Test: Produkt mit Minimum = 0"""
        product = Product(
            id="P003",
            name="Kein Minimum",
            description="Test",
            price=10.0,
            warehouse_qty=1,
            min_stock_level=0,
        )
        assert product.is_low_stock() == False
        product.update_warehouse_qty(-1)
        assert product.warehouse_qty == 0
        assert product.is_low_stock() == False

    def test_product_warehouse_and_shop_transfer(self):
        """Test: Transfer zwischen Warehouse und Shop"""
        product = Product(
            id="P004",
            name="Transfer Test",
            description="Test",
            price=5.0,
            warehouse_qty=100,
            shop_qty=50,
        )
        assert product.get_total_qty() == 150
        
        # Transfer 30 vom Warehouse zum Shop
        product.update_warehouse_qty(-30)
        product.update_shop_qty(30)
        assert product.warehouse_qty == 70
        assert product.shop_qty == 80
        assert product.get_total_qty() == 150  # Gesamt unverändert

    def test_product_with_very_long_name(self):
        """Test: Produkt mit sehr langem Namen"""
        long_name = "A" * 500
        product = Product(
            id="LONG",
            name=long_name,
            description="Test",
            price=1.0,
        )
        assert product.name == long_name
        assert len(product.name) == 500

    def test_product_with_empty_description(self):
        """Test: Produkt mit leerer Beschreibung"""
        product = Product(
            id="P005",
            name="Ohne Beschreibung",
            description="",
            price=5.0,
        )
        assert product.description == ""

    def test_product_with_special_characters_in_name(self):
        """Test: Produkt mit Sonderzeichen im Namen"""
        special_name = "Produkt & Co. (Test) #1 €"
        product = Product(
            id="SPECIAL",
            name=special_name,
            description="Test",
            price=10.0,
        )
        assert product.name == special_name

    def test_product_fractional_price(self):
        """Test: Produkt mit Bruchteilpreis"""
        product = Product(
            id="FRAC",
            name="Cent Artikel",
            description="Test",
            price=0.01,
            warehouse_qty=1000,
        )
        assert product.price == 0.01
        assert product.get_total_value() == 10.0


class TestProductErrorCases:
    """Fehlerfälle für Product-Klasse
    
    Diese Test-Klasse prüft, dass die Product-Klasse mit ungültigen
    oder unmöglichen Eingaben korrekt umgeht (z.B. negative Preise,
    leere IDs) und diese ablehnt.
    """

    def test_product_empty_id(self):
        """Test: Produkt mit leerer ID sollte fehlschlagen"""
        # Versuche Produkt mit leerer ID zu erstellen
        with pytest.raises(ValueError):
            Product(
                id="",  # NULL/leer - sollte nicht erlaubt sein!
                name="Kein ID",
                description="Test",
                price=10.0,
            )

    def test_product_negative_price(self):
        """Test: Produkt mit negativem Preis sollte fehlschlagen"""
        # Versuche Produkt mit negativem Preis zu erstellen
        with pytest.raises(ValueError):
            Product(
                id="P001",
                name="Test",
                description="Test",
                price=-5.0,  # NEGATIV - unmöglich!
            )

    def test_product_negative_warehouse_qty(self):
        """Test: Produkt mit negativem Warehouse-Bestand sollte fehlschlagen"""
        with pytest.raises(ValueError):
            Product(
                id="P001",
                name="Test",
                description="Test",
                price=10.0,
                warehouse_qty=-10,
            )

    def test_product_negative_shop_qty(self):
        """Test: Produkt mit negativem Shop-Bestand sollte fehlschlagen"""
        with pytest.raises(ValueError):
            Product(
                id="P001",
                name="Test",
                description="Test",
                price=10.0,
                shop_qty=-5,
            )

    def test_update_warehouse_qty_below_zero(self):
        """Test: Warehouse-Bestand kann nicht negativ werden"""
        product = Product(
            id="P001",
            name="Test",
            description="Test",
            price=10.0,
            warehouse_qty=10,
        )
        with pytest.raises(ValueError):
            product.update_warehouse_qty(-20)

    def test_update_shop_qty_below_zero(self):
        """Test: Shop-Bestand kann nicht negativ werden"""
        product = Product(
            id="P001",
            name="Test",
            description="Test",
            price=10.0,
            shop_qty=5,
        )
        with pytest.raises(ValueError):
            product.update_shop_qty(-10)

    def test_update_warehouse_qty_with_zero(self):
        """Test: Update mit 0 sollte nichts ändern"""
        product = Product(
            id="P001",
            name="Test",
            description="Test",
            price=10.0,
            warehouse_qty=50,
        )
        product.update_warehouse_qty(0)
        assert product.warehouse_qty == 50

    def test_price_precision_rounding(self):
        """Test: Preisgenauigkeit bei Berechnungen"""
        product = Product(
            id="P001",
            name="Test",
            description="Test",
            price=0.1,
            warehouse_qty=3,
        )
        # 0.1 * 3 kann Floating-Point-Probleme haben
        total_value = product.get_total_value()
        assert abs(total_value - 0.3) < 0.0001


class TestProductStockStatus:
    """Tests für Lagerbestands-Status"""

    def test_stock_status_ok(self):
        """Test: Status OK wenn über Minimum"""
        product = Product(
            id="P001",
            name="Test",
            description="Test",
            price=10.0,
            warehouse_qty=50,
            min_stock_level=10,
        )
        assert product.is_low_stock() == False
        assert "OK" in product.get_stock_status()

    def test_stock_status_critical_exact_minimum(self):
        """Test: Genau am Minimum ist noch OK"""
        product = Product(
            id="P001",
            name="Test",
            description="Test",
            price=10.0,
            warehouse_qty=10,
            min_stock_level=10,
        )
        assert product.is_low_stock() == False

    def test_stock_status_critical_below_minimum(self):
        """Test: Knapp unter Minimum ist kritisch"""
        product = Product(
            id="P001",
            name="Test",
            description="Test",
            price=10.0,
            warehouse_qty=9,
            min_stock_level=10,
        )
        assert product.is_low_stock() == True
        assert "Kritisch" in product.get_stock_status()

    def test_stock_status_critical_zero(self):
        """Test: Bestand = 0 ist kritisch"""
        product = Product(
            id="P001",
            name="Test",
            description="Test",
            price=10.0,
            warehouse_qty=0,
            min_stock_level=10,
        )
        assert product.is_low_stock() == True
