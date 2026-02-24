"""Repository Adapter - In-Memory und persistente Implementierungen"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..domain.product import Product
from ..domain.warehouse import Movement
from ..ports import RepositoryPort


class InMemoryRepository(RepositoryPort):
    """In-Memory Repository - schnell für Tests und schnelle Prototypen"""

    def __init__(self):
        self.products: Dict[str, Product] = {}
        self.movements: List[Movement] = []

    def save_product(self, product: Product) -> None:
        """Produkt im Memory speichern"""
        self.products[product.id] = product

    def load_product(self, product_id: str) -> Optional[Product]:
        """Produkt aus Memory laden"""
        return self.products.get(product_id)

    def load_all_products(self) -> Dict[str, Product]:
        """Alle Produkte aus Memory laden"""
        return self.products.copy()

    def delete_product(self, product_id: str) -> None:
        """Produkt aus Memory löschen"""
        if product_id in self.products:
            del self.products[product_id]

    def save_movement(self, movement: Movement) -> None:
        """Bewegung im Memory speichern"""
        self.movements.append(movement)

    def load_movements(self) -> List[Movement]:
        """Alle Bewegungen aus Memory laden"""
        return self.movements.copy()


class SQLiteRepository(RepositoryPort):
    """SQLite Repository - persistente Speicherung in warehouse.db"""

    def __init__(self, db_path: str = "warehouse.db"):
        self.db_path = str(Path(db_path))
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self) -> None:
        """Tabellen anlegen, wenn sie fehlen."""
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    warehouse_qty INTEGER NOT NULL DEFAULT 0,
                    shop_qty INTEGER NOT NULL DEFAULT 0,
                    sku TEXT,
                    category TEXT,
                    notes TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS movements (
                    id TEXT PRIMARY KEY,
                    product_id TEXT NOT NULL,
                    product_name TEXT,
                    quantity_change INTEGER NOT NULL,
                    movement_type TEXT NOT NULL,
                    reason TEXT,
                    timestamp TEXT,
                    performed_by TEXT,
                    FOREIGN KEY(product_id) REFERENCES products(id)
                )
                """
            )

    # --- helper: datetime <-> text ---
    @staticmethod
    def _dt_to_text(dt: datetime) -> str:
        return dt.isoformat()

    @staticmethod
    def _text_to_dt(value: str) -> datetime:
        return datetime.fromisoformat(value)

    # --- RepositoryPort Implementierung ---

    def save_product(self, product: Product) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO products (
                    id, name, description, price, warehouse_qty, shop_qty, sku, category, notes, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    description=excluded.description,
                    price=excluded.price,
                    warehouse_qty=excluded.warehouse_qty,
                    shop_qty=excluded.shop_qty,
                    sku=excluded.sku,
                    category=excluded.category,
                    notes=excluded.notes,
                    created_at=excluded.created_at,
                    updated_at=excluded.updated_at
                """,
                (
                    product.id,
                    product.name,
                    product.description,
                    float(product.price),
                    int(product.warehouse_qty),
                    int(product.shop_qty),
                    product.sku,
                    product.category,
                    product.notes,
                    self._dt_to_text(product.created_at),
                    self._dt_to_text(product.updated_at),
                ),
            )

    def load_product(self, product_id: str) -> Optional[Product]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM products WHERE id = ?",
                (product_id,),
            ).fetchone()

        if not row:
            return None

        p = Product(
            id=row["id"],
            name=row["name"],
            description=row["description"] or "",
            price=float(row["price"]),
            warehouse_qty=int(row["warehouse_qty"]),
            shop_qty=int(row["shop_qty"]),
            sku=row["sku"] or "",
            category=row["category"] or "",
            notes=row["notes"],
        )

        if row["created_at"]:
            p.created_at = self._text_to_dt(row["created_at"])
        if row["updated_at"]:
            p.updated_at = self._text_to_dt(row["updated_at"])

        return p

    def load_all_products(self) -> Dict[str, Product]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM products").fetchall()

        products: Dict[str, Product] = {}
        for row in rows:
            p = Product(
                id=row["id"],
                name=row["name"],
                description=row["description"] or "",
                price=float(row["price"]),
                warehouse_qty=int(row["warehouse_qty"]),
                shop_qty=int(row["shop_qty"]),
                sku=row["sku"] or "",
                category=row["category"] or "",
                notes=row["notes"],
            )
            if row["created_at"]:
                p.created_at = self._text_to_dt(row["created_at"])
            if row["updated_at"]:
                p.updated_at = self._text_to_dt(row["updated_at"])
            products[p.id] = p

        return products

    def delete_product(self, product_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM products WHERE id = ?", (product_id,))

    def save_movement(self, movement: Movement) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO movements (
                    id, product_id, product_name, quantity_change, movement_type, reason, timestamp, performed_by
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    movement.id,
                    movement.product_id,
                    movement.product_name,
                    int(movement.quantity_change),
                    movement.movement_type,
                    movement.reason,
                    self._dt_to_text(movement.timestamp),
                    movement.performed_by,
                ),
            )

    def load_movements(self) -> List[Movement]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM movements ORDER BY timestamp"
            ).fetchall()

        movements: List[Movement] = []
        for row in rows:
            mv = Movement(
                id=row["id"],
                product_id=row["product_id"],
                product_name=row["product_name"] or "",
                quantity_change=int(row["quantity_change"]),
                movement_type=row["movement_type"],
                reason=row["reason"],
                performed_by=row["performed_by"] or "system",
            )
            if row["timestamp"]:
                mv.timestamp = self._text_to_dt(row["timestamp"])
            movements.append(mv)

        return movements


class RepositoryFactory:
    """Factory für Repository-Instanzen"""

    @staticmethod
    def create_repository(repository_type: str = "memory") -> RepositoryPort:
        """
        Repository basierend auf Typ erstellen

        Args:
            repository_type: "memory" oder andere (z.B. "sqlite")

        Returns:
            RepositoryPort Instanz
        """
        if repository_type == "memory":
            return InMemoryRepository()
        elif repository_type == "sqlite":
            return SQLiteRepository("warehouse.db")
        else:
            raise ValueError(f"Unbekannter Repository-Typ: {repository_type}")
