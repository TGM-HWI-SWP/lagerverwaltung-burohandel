"""Product Domain Model"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Product:
    """
    Basis-Produktklasse für die Lagerverwaltung.
    Siehe docs/DATACLASS_ERKLAERT.md für Erklärung der @dataclass.
    """

    id: str
    name: str
    description: str
    price: float
    warehouse_qty: int = 0
    shop_qty: int = 0
    sku: str = ""
    category: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    notes: Optional[str] = None

    def __post_init__(self):
        """Validierung nach Initialisierung. Siehe docs/DATACLASS_ERKLAERT.md."""
        if not self.id:
            raise ValueError("Product ID kann nicht leer sein")
        if self.price < 0:
            raise ValueError("Preis kann nicht negativ sein")
        if self.warehouse_qty < 0:
            raise ValueError("Lagerbestand kann nicht negativ sein")
        if self.shop_qty < 0:
            raise ValueError("Shopbestand kann nicht negativ sein")

    def update_warehouse_qty(self, amount: int) -> None:
        """
        Lagerbestand aktualisieren

        Args:
            amount: Menge zum Hinzufügen (negativ zum Entnehmen)

        Raises:
            ValueError: wenn die resultierende Menge negativ wäre
        """
        new_quantity = self.warehouse_qty + amount
        if new_quantity < 0:
            raise ValueError(f"Ungültige Lagermenge: {new_quantity}")
        self.warehouse_qty = new_quantity
        self.updated_at = datetime.now()

    def update_shop_qty(self, amount: int) -> None:
        """
        Shopbestand aktualisieren

        Args:
            amount: Menge zum Hinzufügen (negativ zum Entnehmen)

        Raises:
            ValueError: wenn die resultierende Menge negativ wäre
        """
        new_quantity = self.shop_qty + amount
        if new_quantity < 0:
            raise ValueError(f"Ungültige Shopmenge: {new_quantity}")
        self.shop_qty = new_quantity
        self.updated_at = datetime.now()

    def get_total_qty(self) -> int:
        """Gesamtbestand (Warehouse + Shop) abrufen"""
        return self.warehouse_qty + self.shop_qty

    def get_total_value(self) -> float:
        """Gesamtwert des Produktbestands berechnen"""
        return self.price * self.get_total_qty()
