"""Ports - Schnittstellen für externe Abhängigkeiten (Abstraktion)"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from ..domain.product import Product
from ..domain.warehouse import Movement


class RepositoryPort(ABC):
    """Port für Datenpersistenz"""

    @abstractmethod
    def save_product(self, product: Product) -> None:
        """Produkt speichern"""
        raise NotImplementedError

    @abstractmethod
    def load_product(self, product_id: str) -> Optional[Product]:
        """Produkt laden"""
        raise NotImplementedError

    @abstractmethod
    def load_all_products(self) -> Dict[str, Product]:
        """Alle Produkte laden"""
        raise NotImplementedError

    @abstractmethod
    def delete_product(self, product_id: str) -> None:
        """Produkt löschen"""
        raise NotImplementedError

    @abstractmethod
    def save_movement(self, movement: Movement) -> None:
        """Lagerbewegung speichern"""
        raise NotImplementedError

    @abstractmethod
    def load_movements(self) -> List[Movement]:
        """Alle Lagerbewegungen laden"""
        raise NotImplementedError


class ReportPort(ABC):
    """Port für Report-Generierung"""

    @abstractmethod
    def generate_inventory_report(self) -> str:
        """Lagerbestandsbericht generieren"""
        raise NotImplementedError

    @abstractmethod
    def generate_movement_report(self) -> str:
        """Bewegungsprotokoll generieren"""
        raise NotImplementedError
