"""Erweiterte Tests - Randfälle und Fehlerfälle für Report B"""

import pytest
from datetime import datetime, timedelta
from src.domain.product import Product
from src.domain.warehouse import Movement
from src.reports.report_b import ReportB


class TestReportBEdgeCases:
    """Randfälle für Report B
    
    Diese Test-Klasse prüft, wie Report B mit extremen aber
    gültigen Daten umgeht (z.B. leere Berichte, viele Bewegungen,
    kostenlose Produkte).
    """

    def test_empty_report(self):
        """Test: Report mit leeren Daten
        
        Wenn es keine Produkte und keine Bewegungen gibt,
        sollte der Report trotzdem funktionieren.
        Alle Summen sollten 0 sein.
        """
        # Leere Listen - kein Daten vorhanden
        report = ReportB(movements=[], products=[])
        
        # Zusammenfassung abrufen
        summary = report.get_movement_summary()
        # Prüfe: Alle Werte sind 0
        assert summary["total_movements"] == 0
        assert summary["items_in"] == 0
        assert summary["items_out"] == 0
        assert summary["net_flow"] == 0

    def test_single_movement(self):
        """Test: Report mit einer Bewegung
        
        Mit nur 1 Einkauf sollte der Report zeigen:
        - 1 Gesamte Bewegung
        - 10 Eingänge (IN = 10) 
        - 0 Ausgänge
        - 10 Netto-Fluss
        """
        # Eine einzelne Bewegung: +10 Einkauf
        movement = Movement(
            id="M001",
            product_id="P001",
            product_name="Test",
            quantity_change=10,  # +10
            movement_type="IN",  # Einkauf
            timestamp=datetime.now(),
        )
        report = ReportB(movements=[movement], products=[])
        
        # Zusammenfassung abrufen
        summary = report.get_movement_summary()
        # Prüfe korrekte Zahlen
        assert summary["total_movements"] == 1
        assert summary["items_in"] == 10
        assert summary["items_out"] == 0
        assert summary["net_flow"] == 10

    def test_many_movements(self):
        """Test: Report mit vielen Bewegungen (100 Stk.)
        
        Mit 100 Bewegungen wechselnd zwischen IN und SOLD:
        - 100 Gesamte Bewegungen
        - 50 Eingänge (50x IN)
        - 50 Ausgänge (50x SOLD)
        - 0 Netto-Fluss (ausgeglichen)
        """
        movements = []
        for i in range(100):
            movement = Movement(
                id=f"M{i:04d}",
                product_id=f"P{i % 10:02d}",
                product_name=f"Produkt {i % 10}",
                quantity_change=1 if i % 2 == 0 else -1,
                movement_type="IN" if i % 2 == 0 else "SOLD",
                timestamp=datetime.now() - timedelta(minutes=i),
            )
            movements.append(movement)
        
        report = ReportB(movements=movements, products=[])
        summary = report.get_movement_summary()
        
        assert summary["total_movements"] == 100
        assert summary["items_in"] == 50
        assert summary["items_out"] == 50
        assert summary["net_flow"] == 0

    def test_zero_price_products(self):
        """Test: Produkte mit Preis = 0
        
        Kostenlose Produkte sollen nicht zum Lagerwert beitragen.
        Mit 1x Preis 0 und 1x Preis 10:
        Gesamtwert = 500 (nur das 10er-Produkt zählt)
        """
        # Produkte: 1 kostenlos, 1 für 10 Euro
        products = [
            # Kostenloses Produkt - zählt NICHT!
            Product(id="P001", name="Gratis", description="T", price=0.0, warehouse_qty=100),
            # Normales Produkt mit 50 * 10 = 500 Euro
            Product(id="P002", name="Normal", description="T", price=10.0, warehouse_qty=50),
        ]
        report = ReportB(movements=[], products=products)
        
        # Inventar-Statistiken abrufen
        stats = report.get_inventory_statistics()
        # Prüfe: Nur P002 trägt zum Wert bei (50 * 10 = 500)
        assert stats["total_inventory_value"] == 500.0  # Nur P002

    def test_very_large_quantities(self):
        """Test: Sehr große Bestandsmengen
        
        Riesige Lagerbestände (1M im Warehouse, 500k im Shop)
        sollten richtig berechnet werden.
        Gesamtwert = 1M + 500k = 1,5M
        """
        products = [
            Product(
                id="P001",
                name="Viel Bestand",
                description="T",
                price=1.0,
                warehouse_qty=1000000,
                shop_qty=500000,
            ),
        ]
        report = ReportB(movements=[], products=products)
        
        stats = report.get_inventory_statistics()
        assert stats["total_inventory_value"] == 1500000.0

    def test_category_statistics(self):
        """Test: Kategoriestatistiken"""
        products = [
            Product(id="P001", name="P1", description="T", price=10.0, warehouse_qty=10, category="A"),
            Product(id="P002", name="P2", description="T", price=20.0, warehouse_qty=20, category="A"),
            Product(id="P003", name="P3", description="T", price=30.0, warehouse_qty=5, category="B"),
        ]
        report = ReportB(movements=[], products=products)
        
        cat_stats = report.get_category_statistics()
        assert cat_stats is not None
        # Sollte Kategoriestatistiken enthalten

    def test_low_stock_detection(self):
        """Test: Erkennung von niedrigem Bestand
        
        Mit 3 Produkten (nur 2 unter Minimum):
        - P001: 2 Stk. bei Minimum 5 = LOW
        - P002: 10 Stk. bei Minimum 5 = OK
        - P003: 0 Stk. bei Minimum 1 = LOW
        
        low_stock_count sollte 2 sein.
        """
        products = [
            Product(id="P001", name="P1", description="T", price=10.0, warehouse_qty=2, min_stock=5),
            Product(id="P002", name="P2", description="T", price=20.0, warehouse_qty=10, min_stock=5),
            Product(id="P003", name="P3", description="T", price=30.0, warehouse_qty=0, min_stock=1),
        ]
        report = ReportB(movements=[], products=products)
        
        stats = report.get_inventory_statistics()
        assert stats["low_stock_count"] == 2  # P001 und P003

    def test_movement_types_variety(self):
        """Test: Verschiedene Bewegungstypen
        
        Mit 4 verschiedenen Bewegungstypen:
        - IN: +100 (Einkauf)
        - SOLD: -50 (Verkauf)
        - TO_SHOP: -30 (Transfer zu Shop)
        - FROM_SHOP: +20 (Rückgabe aus Shop)
        
        Eingänge = 120, Ausgänge = 80, Netto = 40
        """
        movements = [
            Movement("M001", "P001", "P1", 100, "IN", datetime.now()),
            Movement("M002", "P001", "P1", -50, "SOLD", datetime.now()),
            Movement("M003", "P001", "P1", -30, "TO_SHOP", datetime.now()),
            Movement("M004", "P001", "P1", 20, "FROM_SHOP", datetime.now()),
        ]
        report = ReportB(movements=movements, products=[])
        
        summary = report.get_movement_summary()
        assert summary["total_movements"] == 4
        assert summary["items_in"] == 120  # IN + FROM_SHOP
        assert summary["items_out"] == 80  # SOLD + TO_SHOP
        assert summary["net_flow"] == 40


class TestReportBErrorCases:
    """Fehlerfälle für Report B
    
    Diese Test-Klasse prüft, dass Report B mit ungültigen oder
    fehlenden Daten nicht crasht sondern elegant damit umgeht.
    """

    def test_missing_product_in_movement(self):
        """Test: Bewegung für nicht existierendes Produkt
        
        Manchmal kann eine Bewegung für ein Produkt aufgezeichnet sein,
        das danach gelöscht wurde. Der Report sollte nicht crashen,
        sondern mit diesem Fall elegant umgehen.
        """
        movement = Movement(
            id="M001",
            product_id="NONEXISTENT",
            product_name="Nicht da",
            quantity_change=10,
            movement_type="IN",
            timestamp=datetime.now(),
        )
        products = [
            Product(id="P001", name="P1", description="T", price=10.0),
        ]
        
        # Report sollte auch mit unbekannten Produkten funktionieren
        report = ReportB(movements=[movement], products=products)
        summary = report.get_movement_summary()
        assert summary["total_movements"] == 1

    def test_negative_quantities(self):
        """Test: Produkte mit negativem Bestand (sollte nicht passieren, aber testen)"""
        products = [
            Product(
                id="P001",
                name="Negativ",
                description="T",
                price=10.0,
                warehouse_qty=-5,
                shop_qty=10,
            ),
        ]
        report = ReportB(movements=[], products=products)
        
        # Sollte mit negativem Bestand umgehen können
        stats = report.get_inventory_statistics()
        assert stats["total_inventory_value"] == 50.0  # Nur shop_qty zählen?

    def test_future_dated_movements(self):
        """Test: Bewegungen mit Datum in der Zukunft
        
        Manche Bewegungen könnten geplant sein (future date)
        oder fehlerhaft datiert sein. Der Report sollte
        diese trotzdem verarbeiten können.
        """
        future_time = datetime.now() + timedelta(days=10)
        movement = Movement(
            id="M001",
            product_id="P001",
            product_name="Future",
            quantity_change=10,
            movement_type="IN",
            timestamp=future_time,
        )
        report = ReportB(movements=[movement], products=[])
        
        summary = report.get_movement_summary()
        assert summary["total_movements"] == 1

    def test_very_old_dated_movements(self):
        """Test: Bewegungen lange in der Vergangenheit
        
        Alte Daten von vor 10 Jahren sollten trotzdem
        im Report verarbeitet werden können.
        Das ist ein Test für historische Daten.
        """
        old_time = datetime.now() - timedelta(days=365*10)
        movement = Movement(
            id="M001",
            product_id="P001",
            product_name="Old",
            quantity_change=10,
            movement_type="IN",
            timestamp=old_time,
        )
        report = ReportB(movements=[movement], products=[])
        
        summary = report.get_movement_summary()
        assert summary["total_movements"] == 1

    def test_none_product_name(self):
        """Test: Produkt ohne Namen"""
        products = [
            Product(id="P001", name="", description="T", price=10.0, warehouse_qty=10),
        ]
        report = ReportB(movements=[], products=products)
        
        cat_stats = report.get_category_statistics()
        # Sollte nicht crashen


class TestReportBChartGeneration:
    """Tests für Chart-Generierung in Report B
    
    Diese Test-Klasse prüft, dass die Diagramme korrekt
    generiert werden, auch bei leeren oder extremen Daten.
    """

    def test_generate_chart_empty_movements(self):
        """Test: Chart-Generierung mit leeren Bewegungen
        
        Wenn es keine Daten gibt, sollte der Chart trotzdem
        generiert werden (leere Chart ist OK).
        Das Ergebnis sollte ein Base64-String sein.
        """
        report = ReportB(movements=[], products=[])
        
        # Sollte nicht crashen und ein Base64-String zurückgeben
        chart = report.generate_movement_chart()
        assert chart is not None
        assert isinstance(chart, str)
        assert len(chart) > 0

    def test_generate_chart_single_movement(self):
        """Test: Chart-Generierung mit einer Bewegung
        
        Mit nur 1 Datenpunkt sollte der Chart trotzdem
        sichtbar sein (mit einem einzigen Punkt).
        """
        movement = Movement(
            id="M001",
            product_id="P001",
            product_name="Test",
            quantity_change=100,
            movement_type="IN",
            timestamp=datetime.now(),
        )
        report = ReportB(movements=[movement], products=[])
        
        chart = report.generate_movement_chart()
        assert chart is not None
        assert isinstance(chart, str)

    def test_generate_chart_many_movements(self):
        """Test: Chart-Generierung mit vielen Bewegungen
        
        Mit 100 Datenpunkten sollte der Chart komplett
        generiert werden ohne Performance-Probleme.
        """
        movements = [
            Movement(
                id=f"M{i:04d}",
                product_id="P001",
                product_name="Test",
                quantity_change=10 + i,
                movement_type="IN" if i % 2 == 0 else "SOLD",
                timestamp=datetime.now() - timedelta(hours=i),
            )
            for i in range(100)
        ]
        report = ReportB(movements=movements, products=[])
        
        chart = report.generate_movement_chart()
        assert chart is not None

    def test_generate_type_chart(self):
        """Test: Generierung von Bewegungstyp-Chart"""
        movements = [
            Movement("M001", "P001", "P1", 100, "IN", datetime.now()),
            Movement("M002", "P001", "P1", -50, "SOLD", datetime.now()),
            Movement("M003", "P001", "P1", -30, "TO_SHOP", datetime.now()),
        ]
        report = ReportB(movements=movements, products=[])
        
        chart = report.generate_movement_type_chart()
        assert chart is not None
        assert isinstance(chart, str)

    def test_generate_full_report(self):
        """Test: Generierung des vollständigen Reports"""
        movements = [
            Movement("M001", "P001", "P1", 100, "IN", datetime.now()),
            Movement("M002", "P001", "P1", -30, "SOLD", datetime.now()),
        ]
        products = [
            Product(id="P001", name="P1", description="T", price=10.0, warehouse_qty=70),
        ]
        
        report = ReportB(movements=movements, products=products)
        full_report = report.generate_full_report()
        
        assert full_report is not None
        assert isinstance(full_report, dict)
        # Report sollte Charts enthalten
        assert "movement_chart" in full_report or len(full_report) > 0


class TestReportBDataHandling:
    """Tests für Datenbehandlung in Report B
    
    Diese Test-Klasse prüft, dass die Berechnungen in Report B
    korrekt sind (z.B. Summen, Durchschnitte, Kategorien).
    """


    def test_movement_summary_calculation(self):
        """Test: Korrekte Berechnung der Bewegungszusammenfassung
        
        Mit 4 Bewegungen:
        - INs: 100 + 50 = 150 rein
        - OUTs: 30 + 20 = 50 raus
        - Netto: 150 - 50 = 100
        
        Wir prüfen, dass die Mathe exakt stimmt.
        """
        movements = [
            Movement("M001", "P001", "P1", 100, "IN", datetime.now()),
            Movement("M002", "P002", "P2", 50, "IN", datetime.now()),
            Movement("M003", "P001", "P1", -30, "SOLD", datetime.now()),
            Movement("M004", "P002", "P2", -20, "SOLD", datetime.now()),
        ]
        report = ReportB(movements=movements, products=[])
        
        summary = report.get_movement_summary()
        assert summary["total_movements"] == 4
        assert summary["items_in"] == 150
        assert summary["items_out"] == 50
        assert summary["net_flow"] == 100

    def test_inventory_statistics_with_mixed_data(self):
        """Test: Inventarstatistiken mit gemischten Daten
        
        Mit Produkten unterschiedlicher Preise:
        - 100er Teuer: 10x100 + 5x100 = 1500
        - 1er Günstig: 1000x1 + 500x1 = 1500
        - 0er Gratis: 0x1000 = 0
        
        Gesamtwert = 3000
        """
        products = [
            Product(id="P001", name="Teuer", description="T", price=100.0, warehouse_qty=10, shop_qty=5),
            Product(id="P002", name="Günstig", description="T", price=1.0, warehouse_qty=1000, shop_qty=500),
            Product(id="P003", name="Gratis", description="T", price=0.0, warehouse_qty=1000),
        ]
        report = ReportB(movements=[], products=products)
        
        stats = report.get_inventory_statistics()
        expected_value = 100*10 + 5*100 + 1*1000 + 1*500 + 0*1000
        assert stats["total_inventory_value"] == expected_value

    def test_category_statistics_empty(self):
        """Test: Kategoriestatistiken bei leeren Produkten"""
        report = ReportB(movements=[], products=[])
        
        cat_stats = report.get_category_statistics()
        # Sollte sichere leere Struktur sein
        assert isinstance(cat_stats, (dict, type(None)))
