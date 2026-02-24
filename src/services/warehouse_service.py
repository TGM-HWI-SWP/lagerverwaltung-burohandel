"""Warehouse Service - Geschäftslogik für Lagerverwaltung"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from ..domain.product import Product
from ..domain.warehouse import Movement
from ..ports import RepositoryPort, ReportPort


class WarehouseService:
    """Service für Warehouse-Operationen"""

    def __init__(self, repository: RepositoryPort, report_adapter: ReportPort = None):
        self.repository = repository
        self.report_adapter = report_adapter

    # ===== Produkt-Operationen =====

    def create_product(
        self,
        product_id: str,
        name: str,
        description: str,
        price: float,
        category: str = "",
        warehouse_qty: int = 0,
        shop_qty: int = 0,
        sku: str = "",
        notes: str = "",
    ) -> Product:
        """
        Neues Produkt erstellen und speichern

        Args:
            product_id: Eindeutige Produkt-ID
            name: Produktname
            description: Produktbeschreibung
            price: Preis in €
            category: Produktkategorie
            warehouse_qty: Anfangsbestand im Lager
            shop_qty: Anfangsbestand im Shop
            sku: Stock Keeping Unit
            notes: Weitere Notizen

        Returns:
            Erstelltes Product-Objekt
        """
        product = Product(
            id=product_id,
            name=name,
            description=description,
            price=price,
            warehouse_qty=warehouse_qty,
            shop_qty=shop_qty,
            category=category,
            sku=sku,
            notes=notes,
        )
        self.repository.save_product(product)
        return product

    def get_all_products(self) -> List[Product]:
        """Alle Produkte abrufen"""
        return list(self.repository.load_all_products().values())

    def get_product(self, product_id: str) -> Optional[Product]:
        """Einzelnes Produkt abrufen"""
        return self.repository.load_product(product_id)

    def update_product(self, product: Product) -> None:
        """Produkt aktualisieren"""
        self.repository.save_product(product)

    def delete_product(self, product_id: str) -> None:
        """Produkt löschen"""
        self.repository.delete_product(product_id)

    # ===== Transferoperationen (Warehouse <-> Shop) =====

    def transfer_to_shop(self, product_id: str, quantity: int, reason: str = "") -> bool:
        """
        Produkte vom Lager in den Shop transferieren

        Args:
            product_id: Produkt-ID
            quantity: Menge zum transferieren
            reason: Grund für den Transfer

        Returns:
            True wenn erfolgreich, False sonst
        """
        product = self.repository.load_product(product_id)
        if not product:
            return False

        if product.warehouse_qty < quantity:
            return False

        product.update_warehouse_qty(-quantity)
        product.update_shop_qty(quantity)
        self.repository.save_product(product)

        # Bewegung aufzeichnen
        self._record_movement(
            product_id=product_id,
            product_name=product.name,
            quantity_change=-quantity,
            movement_type="TO_SHOP",
            reason=reason or "Transfer zum Shop",
        )

        return True

    def transfer_to_warehouse(self, product_id: str, quantity: int, reason: str = "") -> bool:
        """
        Produkte vom Shop ins Lager transferieren

        Args:
            product_id: Produkt-ID
            quantity: Menge zum transferieren
            reason: Grund für den Transfer

        Returns:
            True wenn erfolgreich, False sonst
        """
        product = self.repository.load_product(product_id)
        if not product:
            return False

        if product.shop_qty < quantity:
            return False

        product.update_shop_qty(-quantity)
        product.update_warehouse_qty(quantity)
        self.repository.save_product(product)

        # Bewegung aufzeichnen
        self._record_movement(
            product_id=product_id,
            product_name=product.name,
            quantity_change=quantity,
            movement_type="FROM_SHOP",
            reason=reason or "Rücktransfer vom Shop",
        )

        return True

    def create_order(self, product_id: str, quantity: int) -> bool:
        """
        Bestellung erstellen (Produkt aus dem Shop entnehmen)

        Args:
            product_id: Produkt-ID
            quantity: Bestellmenge

        Returns:
            True wenn erfolgreich, False sonst
        """
        product = self.repository.load_product(product_id)
        if not product:
            return False

        if product.shop_qty < quantity:
            return False

        product.update_shop_qty(-quantity)
        self.repository.save_product(product)

        # Bewegung aufzeichnen
        self._record_movement(
            product_id=product_id,
            product_name=product.name,
            quantity_change=-quantity,
            movement_type="ORDER",
            reason="Bestellung",
        )

        return True

    # ===== Bestandsabfragen =====

    def get_total_warehouse_value(self) -> float:
        """Gesamtwert des Lagerbestands berechnen"""
        total = 0.0
        for product in self.repository.load_all_products().values():
            total += product.price * product.warehouse_qty
        return total

    def get_total_shop_value(self) -> float:
        """Gesamtwert des Shopbestands berechnen"""
        total = 0.0
        for product in self.repository.load_all_products().values():
            total += product.price * product.shop_qty
        return total

    def get_total_inventory_value(self) -> float:
        """Gesamtwert aller Bestände berechnen"""
        return self.get_total_warehouse_value() + self.get_total_shop_value()

    def get_products_with_totals(self) -> List[Dict]:
        """Alle Produkte mit berechneten Gesamtwerten abrufen"""
        products = []
        for product in self.get_all_products():
            products.append({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "warehouse_qty": product.warehouse_qty,
                "shop_qty": product.shop_qty,
                "available_total": product.get_total_qty(),
                "category": product.category,
                "sku": product.sku,
                "notes": product.notes,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
            })
        return products

    # ===== Bewegungsprotokoll =====

    def _record_movement(
        self,
        product_id: str,
        product_name: str,
        quantity_change: int,
        movement_type: str,
        reason: str = "",
    ) -> None:
        """Lagerbewegung aufzeichnen"""
        movement = Movement(
            id=str(uuid.uuid4()),
            product_id=product_id,
            product_name=product_name,
            quantity_change=quantity_change,
            movement_type=movement_type,
            reason=reason,
            timestamp=datetime.now(),
            performed_by="web_ui",
        )
        self.repository.save_movement(movement)

    def get_movements(self) -> List[Movement]:
        """Alle Lagerbewegungen abrufen"""
        return self.repository.load_movements()

    # ===== Reports =====

    def generate_inventory_report(self) -> str:
        """Lagerbestandsbericht generieren"""
        if self.report_adapter:
            return self.report_adapter.generate_inventory_report()
        return "Report Adapter nicht konfiguriert."

    def generate_movement_report(self) -> str:
        """Bewegungsprotokoll generieren"""
        if self.report_adapter:
            return self.report_adapter.generate_movement_report()
        return "Report Adapter nicht konfiguriert."
