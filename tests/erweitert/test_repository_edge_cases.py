"""Erweiterte Tests - Randfälle und Fehlerfälle für Repository"""

import pytest
from src.domain.product import Product
from src.adapters.repository import InMemoryRepository


class TestInMemoryRepositoryEdgeCases:
    """Randfälle für InMemoryRepository
    
    Das Repository speichert Produkte in einem Speicher.
    Diese Test-Klasse prüft, dass das Repository mit vielen
    Produkten und Updates korrekt umgeht.
    """

    @pytest.fixture
    def repository(self):
        """Repository Instanz"""
        return InMemoryRepository()

    def test_save_and_retrieve_single_product(self, repository):
        """Test: Speichern und Abrufen eines Produkts
        
        Basis-Test: Wir speichern 1 Produkt und holen es
        danach wieder ab. Alle Daten sollten gleich sein.
        """
        # Produkt erstellen
        product = Product(
            id="P001",
            name="Test Produkt",
            description="Test Description",
            price=10.0,
            warehouse_qty=100,
        )
        # Produkt ins Repository speichern
        repository.save(product)
        
        # Produkt von Repository abrufen
        retrieved = repository.get("P001")
        # Prüfe: Produkt nicht None
        assert retrieved is not None
        # Prüfe: ID stimmt
        assert retrieved.id == "P001"
        # Prüfe: Name stimmt
        assert retrieved.name == "Test Produkt"

    def test_save_and_retrieve_many_products(self, repository):
        """Test: Speichern und Abrufen von vielen Produkten (100 Stk.)
        
        Performance-Test: Das Repository sollte 100 Produkte
        speichern und wieder abrufen ohne Fehler.
        """
        products = []
        for i in range(100):
            product = Product(
                id=f"P{i:04d}",
                name=f"Produkt {i}",
                description="Test",
                price=float(i + 1),
                warehouse_qty=10 * (i + 1),
            )
            products.append(product)
            repository.save(product)

        retrieved = repository.get_all()
        assert len(retrieved) == 100

        for i in range(100):
            product = repository.get(f"P{i:04d}")
            assert product is not None
            assert product.price == float(i + 1)

    def test_update_product_prices(self, repository):
        """Test: Preise von Produkten aktualisieren
        
        Wir speichern ein Produkt, ändern den Preis
        und speichern es erneut. Das Repository sollte
        die neue Version mit dem neuen Preis zeigen.
        """
        product = Product(
            id="P001",
            name="Test",
            description="Test",
            price=10.0,
        )
        repository.save(product)

        # Preis ändern
        product.price = 20.0
        repository.save(product)

        retrieved = repository.get("P001")
        assert retrieved.price == 20.0

    def test_update_product_quantities(self, repository):
        """Test: Mengen von Produkten aktualisieren
        
        Warehouse- und Shop-Mengen sollten updatet werden können.
        Nach dem Update sollte das Repository die neuen Werte zeigen.
        """
        product = Product(
            id="P001",
            name="Test",
            description="Test",
            price=10.0,
            warehouse_qty=100,
            shop_qty=50,
        )
        repository.save(product)

        # Mengen ändern
        product.warehouse_qty = 80
        product.shop_qty = 70
        repository.save(product)

        retrieved = repository.get("P001")
        assert retrieved.warehouse_qty == 80
        assert retrieved.shop_qty == 70

    def test_get_products_by_status(self, repository):
        """Test: Abrufen von Produkten nach Status
        
        Wir speichern mehrere Produkte mit unterschiedlichen
        Bestandsständen (niedrig, mittel, hoch) und prüfen,
        dass alle richtig abgerufen werden können.
        """
        products = [
            Product(id="P001", name="Low", description="T", price=10.0, warehouse_qty=5),
            Product(id="P002", name="Med", description="T", price=10.0, warehouse_qty=50),
            Product(id="P003", name="High", description="T", price=10.0, warehouse_qty=100),
        ]
        for product in products:
            repository.save(product)

        all_products = repository.get_all()
        assert len(all_products) == 3

    def test_delete_product_not_implemented(self, repository):
        """Test: Delete-Methode ist optional (keine Implementierung erforderlich)"""
        # In diesem Repository können wir nicht löschen
        # aber wir können testen, dass get() non-existent zu None führen würde
        assert repository.get("NONEXISTENT") is None


class TestInMemoryRepositoryErrorCases:
    """Fehlerfälle für InMemoryRepository
    
    Diese Test-Klasse prüft, dass das Repository mit ungültigen
    Eingaben (z.B. None, nicht existierende Produkte) richtig umgeht.
    """

    @pytest.fixture
    def repository(self):
        """Repository Instanz"""
        return InMemoryRepository()

    def test_get_nonexistent_product(self, repository):
        """Test: Abrufen eines nicht existierenden Produkts
        
        Wenn wir ein Produkt abrufen, das nicht existiert,
        sollte das Repository None zurükkgeben (nicht crashen).
        """
        result = repository.get("NONEXISTENT")
        assert result is None

    def test_save_none(self, repository):
        """Test: Speichern von None sollte fehlschlagen
        
        Sicherheitscheck: Das Repository sollte None nicht
        akzeptieren. Das würde zu Fehlern führen.
        """
        with pytest.raises((TypeError, ValueError, AttributeError)):
            repository.save(None)

    def test_get_empty_repository(self, repository):
        """Test: Abrufen aller Produkte aus leerem Repository
        
        Ein neues, gefülltes Repository sollte leer sein.
        get_all() sollte eine leere Liste zurückgeben.
        """
        products = repository.get_all()
        assert len(products) == 0

    def test_update_product_after_removal_from_list(self, repository):
        """Test: Produkt noch aktualisierbar nach Änderung"""
        product = Product(id="P001", name="Test", description="T", price=10.0)
        repository.save(product)

        # Original-Referenz ändern
        product.price = 20.0
        repository.save(product)

        # über Repository abrufen sollte neue Version zeigen
        retrieved = repository.get("P001")
        assert retrieved.price == 20.0

    def test_duplicate_id_overwrites(self, repository):
        """Test: Gleiches ID überschreibt älteres Produkt
        
        Wenn wir 2 Produkte mit gleicher ID speichern,
        sollte die neuere Version die ältere ersetzen.
        Es sollte nur noch 1 Produkt mit dieser ID geben.
        """
        # Produkt 1 mit ID "P001"
        product1 = Product(id="P001", name="Produkt 1", description="T", price=10.0)
        # Produkt 2 auch mit ID "P001" (DUPLIKAT!)
        product2 = Product(id="P001", name="Produkt 2", description="T", price=20.0)

        # Beide nacheinander speichern
        repository.save(product1)
        repository.save(product2)  # Das sollte das erste überschreiben!

        # Abrufen - sollte neuere Version sein (Produkt 2)
        retrieved = repository.get("P001")
        # Prüfe: Name sollte "Produkt 2" sein
        assert retrieved.name == "Produkt 2"
        # Prüfe: Preis sollte 20 sein
        assert retrieved.price == 20.0

        # Prüfe: Es gibt nur 1 Produkt mit P001 (nicht 2!)
        all_products = repository.get_all()
        p001_count = sum(1 for p in all_products if p.id == "P001")
        assert p001_count == 1


class TestRepositoryDataIntegrity:
    """Tests für Datenintegrität im Repository
    
    Diese Test-Klasse prüft, dass das Repository Daten
    korrekt speichert und abruft, auch bei extremen Werten
    (sehr große Preise, sehr lange Texte, Sonderzeichen).
    """

    @pytest.fixture
    def repository(self):
        """Repository Instanz"""
        return InMemoryRepository()

    def test_price_zero_handling(self, repository):
        """Test: Produkt mit Preis = 0
        
        Kostenlose Produkte sind erlaubt.
        Das Repository sollte diese speichern und abrufen können.
        """
        product = Product(
            id="P001",
            name="Kostenlos",
            description="Test",
            price=0.0,
        )
        repository.save(product)
        retrieved = repository.get("P001")
        assert retrieved.price == 0.0

    def test_price_very_small(self, repository):
        """Test: Produkt mit sehr kleinem Preis (0.01)
        
        Sehr günstige Produkte mit Zentbeträgen sollten
        ohne Rundungsfehler gespeichert werden.
        """
        product = Product(
            id="P001",
            name="Günstig",
            description="Test",
            price=0.01,
        )
        repository.save(product)
        retrieved = repository.get("P001")
        assert abs(retrieved.price - 0.01) < 0.001

    def test_price_very_large(self, repository):
        """Test: Produkt mit sehr großem Preis (999.999,99)
        
        Sehr teure Produkte sollten ohne Datenverlust
        gespeichert und abgerufen werden.
        """
        product = Product(
            id="P001",
            name="Teuer",
            description="Test",
            price=999999.99,
        )
        repository.save(product)
        retrieved = repository.get("P001")
        assert retrieved.price == 999999.99

    def test_quantity_zero(self, repository):
        """Test: Produkt mit Menge = 0
        
        Ausverkaufte Produkte (Bestand = 0) sollten
        speichbar sein und bund abrufbar sein.
        """
        product = Product(
            id="P001",
            name="Ausverkauft",
            description="Test",
            price=10.0,
            warehouse_qty=0,
            shop_qty=0,
        )
        repository.save(product)
        retrieved = repository.get("P001")
        assert retrieved.warehouse_qty == 0
        assert retrieved.shop_qty == 0

    def test_quantity_very_large(self, repository):
        """Test: Produkt mit sehr großer Menge
        
        Riesige Lagerbestände (1 Million) sollten richtig
        gespeichert und abgerufen werden.
        """
        product = Product(
            id="P001",
            name="Viel",
            description="Test",
            price=10.0,
            warehouse_qty=1000000,
            shop_qty=500000,
        )
        repository.save(product)
        retrieved = repository.get("P001")
        assert retrieved.warehouse_qty == 1000000
        assert retrieved.shop_qty == 500000

    def test_special_characters_in_strings(self, repository):
        """Test: Spezialzeichen in Text-Feldern
        
        Produkte können Namen mit Umlauten, Sonderzeichen,
        Anführungszeichen haben. Diese sollten richtig gespeichert
        und abgerufen werden.
        """
        product = Product(
            id="P-001/2024",
            name="Produkt mit Ümlaut & Spezialzeichen: <>&",
            description="Beschreibung mit 'Anführungszeichen' und \"Doppel\"",
            price=10.0,
        )
        repository.save(product)
        retrieved = repository.get("P-001/2024")
        assert retrieved.id == "P-001/2024"
        assert "Ümlaut & Spezialzeichen" in retrieved.name
        assert "Anführungszeichen" in retrieved.description

    def test_very_long_strings(self, repository):
        """Test: Sehr lange Text-Felder
        
        Wenn Namen oder Beschreibungen sehr lang sind (1000+ Zeichen),
        sollte das Repository diese trotzdem speichern können.
        """
        long_name = "A" * 1000
        long_description = "B" * 2000
        product = Product(
            id="P001",
            name=long_name,
            description=long_description,
            price=10.0,
        )
        repository.save(product)
        retrieved = repository.get("P001")
        assert len(retrieved.name) == 1000
        assert len(retrieved.description) == 2000
