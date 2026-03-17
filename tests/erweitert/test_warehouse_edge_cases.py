"""Erweiterte Tests - Randfälle u. Fehlerfälle für Warehouse und WarehouseService"""

import pytest
from datetime import datetime
from src.domain.product import Product
from src.domain.warehouse import Warehouse, Movement
from src.adapters.repository import InMemoryRepository
from src.services import WarehouseService


class TestWarehouseEdgeCases:
    """Randfälle für Warehouse-Klasse
    
    Diese Test-Klasse prüft, wie das Warehouse mit extremen
    aber gültigen Situationen umgeht (z.B. leeres Lager,
    viele Produkte, viele Bewegungen).
    """

    def test_warehouse_empty(self):
        """Test: Neues leeres Warehouse
        
        Wir prüfen, dass ein neues Warehouse leer ist.
        Es sollte 0 Produkte und 0 Bewegungen haben.
        Der Gesamtwert sollte 0 sein.
        """
        # Neues leeres Warehouse erstellen
        warehouse = Warehouse("Lager 1")
        
        # Prüfe: Keine Produkte vorhanden
        assert len(warehouse.products) == 0
        # Prüfe: Keine Bewegungen vorhanden
        assert len(warehouse.movements) == 0
        # Prüfe: Gesamtwert ist 0
        assert warehouse.get_total_inventory_value() == 0.0

    def test_warehouse_single_product(self):
        """Test: Warehouse mit genau einem Produkt
        
        Wir prüfen, dass ein Produkt korrekt hinzugefügt wird
        und der Gesamtwert richtig berechnet wird (100 * 10 = 1000).
        """
        # Neues Warehouse erstellen
        warehouse = Warehouse("Lager 1")
        # Produkt mit Preis 10 und Menge 100 erstellen
        product = Product(
            id="P001",
            name="Test",
            description="Test",
            price=10.0,
            warehouse_qty=100,
        )
        # Produkt zum Warehouse hinzufügen
        warehouse.add_product(product)
        
        # Prüfe: 1 Produkt vorhanden
        assert len(warehouse.products) == 1
        # Prüfe: Produkt P001 existiert
        assert warehouse.get_product("P001") is not None
        # Prüfe: Gesamtwert = 100 * 10 = 1000
        assert warehouse.get_total_inventory_value() == 1000.0

    def test_warehouse_many_products(self):
        """Test: Warehouse mit vielen Produkten (1000 Stk.)
        
        Wir prüfen, dass das Warehouse viele Produkte gleichzeitig
        speichern kann. Der Gesamtwert sollte korrekt summiert werden:
        (1*10) + (2*10) + (3*10) + ... + (1000*10)
        """
        # Neues Warehouse erstellen
        warehouse = Warehouse("Lager 1")
        # 1000 Produkte nacheinander hinzufügen
        for i in range(1000):
            product = Product(
                id=f"P{i:04d}",
                name=f"Produkt {i}",
                description="Test",
                # Preis steigt: 1, 2, 3, ... 1000
                price=float(i + 1),
                # Alle haben Menge 10
                warehouse_qty=10,
            )
            warehouse.add_product(product)
        
        # Prüfe: Genau 1000 Produkte vorhanden
        assert len(warehouse.products) == 1000
        # Berechne erwarteten Gesamtwert
        # = Sum(Preis[i] * Menge[i]) für i=0..999
        # = Sum((i+1)*10) für i=0..999
        expected_value = sum((i + 1) * 10 for i in range(1000))
        # Prüfe: Gesamtwert stimmt
        assert warehouse.get_total_inventory_value() == expected_value

    def test_warehouse_multiple_movements(self):
        """Test: Warehouse mit vielen Bewegungen (100 Stk.)
        
        Wir prüfen, dass das Warehouse alle Bewegungen korrekt
        speichert und die Geschichte jeder Transaktion verwaltet.
        """
        # Neues Warehouse erstellen
        warehouse = Warehouse("Lager 1")
        # Produkt mit großem Bestand erstellen
        product = Product(
            id="P001",
            name="Test",
            description="Test",
            price=10.0,
            warehouse_qty=1000,
        )
        warehouse.add_product(product)

        # 100 Bewegungen aufzeichnen
        for i in range(100):
            movement = Movement(
                id=f"M{i:04d}",
                product_id="P001",
                product_name="Test",
                quantity_change=1,
                movement_type="IN",
                timestamp=datetime.now(),
            )
            warehouse.record_movement(movement)

        # Prüfe: Alle 100 Bewegungen gespeichert
        assert len(warehouse.movements) == 100

    def test_movement_with_negative_change(self):
        """Test: Bewegung mit negativer Mengenänderung
        
        Negative Mengen sind normal (z.B. Verkauf = -50).
        Wir prüfen, dass das Warehouse damit umgehen kann.
        """
        # Neues Warehouse mit Produkt
        warehouse = Warehouse("Lager 1")
        product = Product(
            id="P001",
            name="Test",
            description="Test",
            price=10.0,
            warehouse_qty=100,
        )
        warehouse.add_product(product)

        # Bewegung mit NEGATIVER Menge (Verkauf)
        movement = Movement(
            id="M001",
            product_id="P001",
            product_name="Test",
            quantity_change=-50,  # Verkauf = minus!
            movement_type="SOLD",
            timestamp=datetime.now(),
        )
        warehouse.record_movement(movement)
        
        # Prüfe: Bewegung wurde gespeichert
        assert len(warehouse.movements) == 1


class TestWarehouseErrorCases:
    """Fehlerfälle für Warehouse-Klasse
    
    Diese Test-Klasse prüft, dass das Warehouse mit ungültigen
    Situationen korrekt umgeht und diese ablehnt.
    """

    def test_add_duplicate_product(self):
        """Test: Doppeltes Produkt mit gleicher ID sollte fehlschlagen
        
        Jedes Produkt sollte eine eindeutige ID haben.
        Wir dürfen nicht 2 Produkte mit der gleichen ID hinzufügen.
        """
        # Neues Warehouse
        warehouse = Warehouse("Lager 1")
        # Produkt 1 mit ID "P001"
        product1 = Product(
            id="P001",
            name="Produkt 1",
            description="Test",
            price=10.0,
        )
        # Produktt 2 auch mit ID "P001" (DUPLIKAT!)
        product2 = Product(
            id="P001",
            name="Produkt 2",
            description="Test",
            price=20.0,
        )
        # Erstes Produkt hinzufügen - OK
        warehouse.add_product(product1)
        # Zweites Produkt hinzufügen - sollte ERROR werfen!
        with pytest.raises(ValueError):
            warehouse.add_product(product2)

    def test_record_movement_nonexistent_product(self):
        """Test: Bewegung für nicht existierendes Produkt sollte fehlschlagen
        
        Wir können keine Bewegung für ein Produkt aufzeichnen,
        das nicht im Warehouse gespeichert ist.
        """
        # Neues leeres Warehouse (keine Produkte!)
        warehouse = Warehouse("Lager 1")
        # Bewegung für nicht existierendes Produkt P999
        movement = Movement(
            id="M001",
            product_id="P999",  # Dieses Produkt existiert nicht!
            product_name="Nicht existierend",
            quantity_change=10,
            movement_type="IN",
            timestamp=datetime.now(),
        )
        # Bewegung aufzeichnen - sollte ERROR werfen!
        with pytest.raises(ValueError):
            warehouse.record_movement(movement)


class TestWarehouseServiceEdgeCases:
    """Randfälle für WarehouseService
    
    Diese Test-Klasse prüft komplexe Operationen wie Transfers
    und Verkäufe unter extremen aber gültigen Bedingungen.
    WarehouseService ist die Schicht, die Business-Logik enthält.
    """

    @pytest.fixture
    def service(self):
        """Service mit In-Memory Repository"""
        repository = InMemoryRepository()
        return WarehouseService(repository)

    def test_transfer_to_shop_exact_amount(self):
        """Test: Transfer exakt die gesamte Menge vom Lager zum Shop
        
        Wir prüfen, dass wenn wir ALLE Produkte von
        Warehouse zu Shop transferieren, funktioniert das korrekt.
        Nachher: Warehouse = 0, Shop = 100
        """
        service = self.service
        # Produkt mit 100 im Warehouse erstellen
        service.create_product("P001", "Test", "Test", 10.0, warehouse_qty=100)
        
        # Transfer ALLE 100 vom Warehouse zum Shop
        result = service.transfer_to_shop("P001", 100)
        # Sollte erfolgreich sein
        assert result == True
        
        # Prüfe neuen Bestand
        product = service.get_product("P001")
        # Warehouse sollte jetzt leer sein
        assert product.warehouse_qty == 0
        # Shop sollte alle 100 haben
        assert product.shop_qty == 100

    def test_transfer_to_warehouse_exact_amount(self):
        """Test: Transfer exakt die gesamte Menge vom Shop zum Lager
        
        Umgekehrte Operation: Von Shop zu Warehouse.
        Nachher: Warehouse = 50, Shop = 0
        """
        service = self.service
        service.create_product("P001", "Test", "Test", 10.0, shop_qty=50)
        
        result = service.transfer_to_warehouse("P001", 50)
        assert result == True
        
        product = service.get_product("P001")
        assert product.warehouse_qty == 50
        assert product.shop_qty == 0

    def test_sell_product_last_unit(self):
        """Test: Verkauf der letzten Einheit
        
        Wir prüfen, dass der Verkauf der letzten Einheit funktioniert.
        Nachher sollte Shop-Bestand = 0 sein.
        """
        service = self.service
        service.create_product("P001", "Test", "Test", 10.0, shop_qty=1)
        
        result = service.sell_product("P001", 1)
        assert result == True
        
        product = service.get_product("P001")
        assert product.shop_qty == 0

    def test_multiple_movements_sequence(self):
        """Test: Sequenz von mehreren Bewegungen
        
        Dies ist ein realistisches Szenario: 
        1. Einkauf (+50 ins Warehouse) 
        2. Transfer zum Shop (50 zum Shop)
        3. Verkauf (-30 aus Shop)
        4. Rückgabe zum Warehouse (+20 zurück)
        
        Wir prüfen, dass alle Vorgänge korrekt nacheinander
        ausgeführt werden und die Bezüge stimmen.
        """
        service = self.service
        service.create_product("P001", "Test", "Test", 10.0, warehouse_qty=100)
        
        # Einkauf
        service.create_purchase("P001", 50)
        product = service.get_product("P001")
        assert product.warehouse_qty == 150
        
        # Transfer
        service.transfer_to_shop("P001", 50)
        product = service.get_product("P001")
        assert product.warehouse_qty == 100
        assert product.shop_qty == 50
        
        # Verkauf
        service.sell_product("P001", 30)
        product = service.get_product("P001")
        assert product.shop_qty == 20
        
        # Rücktransfer
        service.transfer_to_warehouse("P001", 20)
        product = service.get_product("P001")
        assert product.warehouse_qty == 120
        assert product.shop_qty == 0

    def test_get_movements_order(self):
        """Test: Bewegungen werden in chronologischer Reihenfolge gespeichert
        
        Die Reihenfolge der Transaktionen ist wichtig für die History.
        Wir prüfen, dass die Bewegungen in der richtigen
        Reihenfolge (zeitlich) gespeichert sind.
        """
        service = self.service
        service.create_product("P001", "Test", "Test", 10.0, warehouse_qty=100, shop_qty=0)
        
        # Mehrere Operationen
        service.create_purchase("P001", 10)
        service.transfer_to_shop("P001", 5)
        service.sell_product("P001", 3)
        
        movements = service.get_movements()
        assert len(movements) == 3
        assert movements[0].movement_type == "IN"
        assert movements[1].movement_type == "TO_SHOP"
        assert movements[2].movement_type == "SOLD"


class TestWarehouseServiceErrorCases:
    """Fehlerfälle für WarehouseService
    
    Diese Test-Klasse prüft, dass WarehouseService ungültige
    Operationen ablehnt (z.B. mehr verkaufen als vorhanden).
    """

    @pytest.fixture
    def service(self):
        """Service mit In-Memory Repository"""
        repository = InMemoryRepository()
        return WarehouseService(repository)

    def test_transfer_more_than_available(self):
        """Test: Transfer mehr als verfügbar sollte fehlschlagen
        
        Sicherheitscheck: Wenn weniger als 100 vorhanden sind,
        sollte der Transfer von 100 abgelehnt werden (return False).
        Der Bestand sollte unverändert bleiben.
        """
        service = self.service
        # Produkt mit nur 50 im Warehouse erstellen
        service.create_product("P001", "Test", "Test", 10.0, warehouse_qty=50)
        
        # Versuche 100 zu transferieren (aber nur 50 vorhanden!)
        result = service.transfer_to_shop("P001", 100)
        # Sollte fehlschlagen!
        assert result == False
        
        # Prüfe: Bestand sollte UNVERÄNDERT bleiben
        product = service.get_product("P001")
        # Immer noch 50 im Warehouse
        assert product.warehouse_qty == 50
        # Immer noch 0 im Shop
        assert product.shop_qty == 0

    def test_sell_more_than_available(self):
        """Test: Verkauf mehr als verfügbar sollte fehlschlagen
        
        Sicherheitscheck: Wir können nicht mehr verkaufen
        als vorhanden ist. Der Verkauf sollte abgelehnt werden.
        """
        service = self.service
        service.create_product("P001", "Test", "Test", 10.0, shop_qty=20)
        
        result = service.sell_product("P001", 50)
        assert result == False
        
        # Bestand sollte unverändert sein
        product = service.get_product("P001")
        assert product.shop_qty == 20

    def test_create_purchase_zero_quantity(self):
        """Test: Einkauf mit Menge = 0 sollte fehlschlagen
        
        Es macht keinen Sinn, 0 Einheiten zu kaufen.
        Dies sollte abgelehnt werden.
        """
        service = self.service
        service.create_product("P001", "Test", "Test", 10.0)
        
        result = service.create_purchase("P001", 0)
        assert result == False

    def test_create_purchase_negative_quantity(self):
        """Test: Einkauf mit negativer Menge sollte fehlschlagen
        
        Ein negativer Einkauf macht keinen Sinn (das wäre ein Verkauf).
        Dies sollte abgelehnt werden.
        """
        service = self.service
        service.create_product("P001", "Test", "Test", 10.0)
        
        result = service.create_purchase("P001", -10)
        assert result == False

    def test_operation_on_nonexistent_product(self):
        """Test: Operation auf nicht existierendes Produkt sollte fehlschlagen
        
        Wir können keine Operationen auf Produkte machen,
        die nicht im System existieren.
        """
        service = self.service
        
        assert service.transfer_to_shop("NONEXISTENT", 10) == False
        assert service.sell_product("NONEXISTENT", 10) == False
        assert service.create_purchase("NONEXISTENT", 10) == False
