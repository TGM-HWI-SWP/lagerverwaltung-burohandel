"""Report B - Bewegungsprotokoll und Lagerverlauf-Statistiken"""

import io
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict, Counter

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams

# Matplotlib auf non-interactive backend setzen für Web-Nutzung
plt.switch_backend('Agg')
rcParams['figure.figsize'] = (12, 6)
rcParams['font.size'] = 9


class ReportB:
    """Report B: Bewegungsprotokoll und Lagerverlauf-Statistiken"""

    def __init__(self, movements: List, products: List[Dict]):
        """
        Initialisiere Report B

        Args:
            movements: Liste von Movement-Objekten
            products: Liste von Product-Dicts mit Bestandsinformationen
        """
        self.movements = sorted(movements, key=lambda m: m.timestamp) if movements else []
        self.products = {p['id']: p for p in products} if products else {}

    # ===== BEWEGUNGSPROTOKOLL ANALYSEN =====

    def get_movement_summary(self) -> Dict:
        """
        Grundlegende Statistiken über Lagerbewegungen

        Returns:
            Dictionary mit Bewegungsstatistiken
        """
        if not self.movements:
            return {
                "total_movements": 0,
                "by_type": {},
                "by_date": {},
                "total_items_in": 0,
                "total_items_out": 0,
                "net_flow": 0,
            }

        movement_types = Counter()
        by_date = defaultdict(int)
        total_in = 0
        total_out = 0

        for movement in self.movements:
            movement_types[movement.movement_type] += 1
            date_str = movement.timestamp.strftime("%Y-%m-%d")
            by_date[date_str] += 1

            if movement.quantity_change > 0:
                total_in += movement.quantity_change
            else:
                total_out += abs(movement.quantity_change)

        return {
            "total_movements": len(self.movements),
            "by_type": dict(movement_types),
            "by_date": dict(sorted(by_date.items())),
            "total_items_in": total_in,
            "total_items_out": total_out,
            "net_flow": total_in - total_out,
            "first_date": self.movements[0].timestamp if self.movements else None,
            "last_date": self.movements[-1].timestamp if self.movements else None,
        }

    def get_movements_by_product(self) -> Dict[str, List]:
        """
        Lagerbewegungen nach Produkt gruppieren

        Returns:
            Dictionary mit Produkten und deren Bewegungen
        """
        grouped = defaultdict(list)
        for movement in self.movements:
            grouped[movement.product_id].append({
                "timestamp": movement.timestamp,
                "product_name": movement.product_name,
                "quantity_change": movement.quantity_change,
                "movement_type": movement.movement_type,
                "reason": movement.reason,
            })
        return dict(grouped)

    def get_movement_details(self, limit: int = 50) -> List[Dict]:
        """
        Detailliertes Bewegungsprotokoll mit neuesten Einträgen zuerst

        Args:
            limit: Anzahl der anzuzeigenden Bewegungen

        Returns:
            Liste von Bewegungs-Dicts
        """
        movements_list = []
        for movement in reversed(self.movements[-limit:]):
            movements_list.append({
                "timestamp": movement.timestamp.strftime("%d.%m.%Y %H:%M:%S"),
                "timestamp_iso": movement.timestamp.isoformat(),
                "product_id": movement.product_id,
                "product_name": movement.product_name,
                "quantity_change": movement.quantity_change,
                "movement_type": movement.movement_type,
                "type_display": self._get_movement_type_display(movement.movement_type),
                "reason": movement.reason,
                "performed_by": movement.performed_by,
            })
        return movements_list

    @staticmethod
    def _get_movement_type_display(movement_type: str) -> str:
        """Bewegungstyp in lesbares Format konvertieren"""
        type_map = {
            "IN": "📥 Einkauf",
            "OUT": "📤 Auslieferung",
            "TO_SHOP": "🏬 Zum Shop",
            "FROM_SHOP": "📦 Vom Shop",
            "SOLD": "💳 Verkauf",
            "CORRECTION": "🔧 Korrektur",
        }
        return type_map.get(movement_type, movement_type)

    # ===== LAGERVERLAUF STATISTIKEN =====

    def get_inventory_statistics(self) -> Dict:
        """
        Lagerverlauf-Statistiken und aktuelle Bestandssituation

        Returns:
            Dictionary mit Lagerverlauf-Daten
        """
        if not self.products:
            return {}

        total_value = 0.0
        by_category = defaultdict(float)
        low_stock_count = 0

        for product in self.products.values():
            value = product.get("price", 0) * product.get("available_total", 0)
            total_value += value

            category = product.get("category", "Unbeantwortet")
            by_category[category] += value

            if product.get("is_low_stock", False):
                low_stock_count += 1

        return {
            "total_inventory_value": total_value,
            "total_products": len(self.products),
            "by_category": dict(sorted(by_category.items(), key=lambda x: x[1], reverse=True)),
            "low_stock_count": low_stock_count,
            "categories": list(by_category.keys()),
            "total_warehouse_qty": sum(p.get("warehouse_qty", 0) for p in self.products.values()),
            "total_shop_qty": sum(p.get("shop_qty", 0) for p in self.products.values()),
        }

    def get_category_statistics(self) -> List[Dict]:
        """
        Detaillierte Statistik pro Kategorie

        Returns:
            Liste von Kategorie-Statistiken
        """
        by_category = defaultdict(lambda: {
            "count": 0,
            "total_qty": 0,
            "total_value": 0,
            "products": [],
        })

        for product in self.products.values():
            category = product.get("category", "Unbeantwortet")
            by_category[category]["count"] += 1
            by_category[category]["total_qty"] += product.get("available_total", 0)
            by_category[category]["total_value"] += product.get("price", 0) * product.get("available_total", 0)
            by_category[category]["products"].append({
                "id": product.get("id"),
                "name": product.get("name"),
                "qty": product.get("available_total", 0),
                "value": product.get("price", 0) * product.get("available_total", 0),
            })

        result = []
        for category, stats in sorted(by_category.items(), key=lambda x: x[1]["total_value"], reverse=True):
            result.append({
                "category": category,
                "product_count": stats["count"],
                "total_qty": stats["total_qty"],
                "total_value": stats["total_value"],
                "avg_value_per_product": stats["total_value"] / stats["count"] if stats["count"] > 0 else 0,
            })

        return result

    # ===== VISUALISIERUNGEN =====

    def generate_movement_chart(self) -> str:
        """
        Lagerbewegungen über Zeit visualisieren

        Returns:
            Base64 enkodiertes PNG-Chart
        """
        if not self.movements:
            return ""

        fig, ax = plt.subplots(figsize=(12, 6))

        # Bewegungen pro Tag gruppieren
        by_date = defaultdict(int)
        for movement in self.movements:
            date_str = movement.timestamp.strftime("%Y-%m-%d")
            by_date[date_str] += 1

        dates = sorted(by_date.keys())
        counts = [by_date[d] for d in dates]

        # Chart zeichnen
        ax.plot(dates, counts, marker='o', linestyle='-', linewidth=2, markersize=6, color='steelblue')
        ax.fill_between(range(len(dates)), counts, alpha=0.3, color='steelblue')

        ax.set_xlabel('Datum', fontweight='bold')
        ax.set_ylabel('Anzahl Bewegungen', fontweight='bold')
        ax.set_title('Lagerbewegungen pro Tag', fontweight='bold', fontsize=12)
        ax.grid(True, alpha=0.3)

        # X-Achse formatieren
        if len(dates) > 1:
            ax.set_xticks(range(0, len(dates), max(1, len(dates) // 10)))
            ax.set_xticklabels([dates[i] for i in range(0, len(dates), max(1, len(dates) // 10))], rotation=45)

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def generate_movement_type_chart(self) -> str:
        """
        Lagerbewegungen nach Typ visualisieren

        Returns:
            Base64 enkodiertes PNG-Chart
        """
        if not self.movements:
            return ""

        movement_types = Counter()
        for movement in self.movements:
            movement_types[movement.movement_type] += 1

        fig, ax = plt.subplots(figsize=(10, 6))

        types = [self._get_movement_type_display(t) for t in movement_types.keys()]
        counts = list(movement_types.values())
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']

        bars = ax.bar(types, counts, color=colors[:len(types)], edgecolor='black', linewidth=1.5)

        # Beschriftungen auf Balken
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                   f'{int(count)}',
                   ha='center', va='bottom', fontweight='bold')

        ax.set_ylabel('Anzahl', fontweight='bold')
        ax.set_title('Lagerbewegungen nach Typ', fontweight='bold', fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45, ha='right')

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def generate_inventory_value_chart(self) -> str:
        """
        Bestandswert nach Kategorie visualisieren

        Returns:
            Base64 enkodiertes PNG-Chart
        """
        stats = self.get_inventory_statistics()
        by_category = stats.get("by_category", {})

        if not by_category:
            return ""

        fig, ax = plt.subplots(figsize=(10, 6))

        categories = list(by_category.keys())
        values = list(by_category.values())
        colors = plt.cm.Set3(range(len(categories)))

        wedges, texts, autotexts = ax.pie(values, labels=categories, autopct='%1.1f%%',
                                           colors=colors, startangle=90, textprops={'fontsize': 9})

        # Farbliche Hervorhebung anpassen
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title('Bestandswert nach Kategorie', fontweight='bold', fontsize=12)

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def generate_warehouse_vs_shop_chart(self) -> str:
        """
        Lagervs. Shop-Bestand visualisieren

        Returns:
            Base64 enkodiertes PNG-Chart
        """
        stats = self.get_inventory_statistics()
        warehouse_qty = stats.get("total_warehouse_qty", 0)
        shop_qty = stats.get("total_shop_qty", 0)

        fig, ax = plt.subplots(figsize=(8, 6))

        locations = ['Lager', 'Shop']
        quantities = [warehouse_qty, shop_qty]
        colors = ['#3498db', '#e74c3c']

        bars = ax.bar(locations, quantities, color=colors, edgecolor='black', linewidth=2)

        # Beschriftungen auf Balken
        for bar, qty in zip(bars, quantities):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                   f'{int(qty)}',
                   ha='center', va='bottom', fontweight='bold', fontsize=12)

        ax.set_ylabel('Menge', fontweight='bold')
        ax.set_title('Bestand: Lager vs. Shop', fontweight='bold', fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def generate_movement_quantity_chart(self) -> str:
        """
        Bewegungs-Mengen über Zeit (kumulativ)

        Returns:
            Base64 enkodiertes PNG-Chart
        """
        if not self.movements:
            return ""

        # Kumuliere Bewegungsmengen pro Tag
        by_date = defaultdict(int)
        for movement in self.movements:
            date_str = movement.timestamp.strftime("%Y-%m-%d")
            by_date[date_str] += movement.quantity_change

        dates = sorted(by_date.keys())
        quantities = [by_date[d] for d in dates]

        # Kumulativ berechnen
        cumulative = []
        total = 0
        for qty in quantities:
            total += qty
            cumulative.append(total)

        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(dates, cumulative, marker='o', linestyle='-', linewidth=2.5, markersize=6,
               color='#2ecc71', label='Kumulativ')
        ax.fill_between(range(len(dates)), cumulative, alpha=0.3, color='#2ecc71')

        # Nulllinie
        ax.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)

        ax.set_xlabel('Datum', fontweight='bold')
        ax.set_ylabel('Kumulierte Menge', fontweight='bold')
        ax.set_title('Kumulierte Bestands-Bewegungen', fontweight='bold', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()

        if len(dates) > 1:
            ax.set_xticks(range(0, len(dates), max(1, len(dates) // 10)))
            ax.set_xticklabels([dates[i] for i in range(0, len(dates), max(1, len(dates) // 10))], rotation=45)

        plt.tight_layout()
        return self._fig_to_base64(fig)

    @staticmethod
    def _fig_to_base64(fig) -> str:
        """
        Matplotlib Figure in Base64 PNG konvertieren

        Args:
            fig: Matplotlib Figure-Objekt

        Returns:
            Base64 enkodierter PNG-String
        """
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)
        return image_base64

    # ===== REPORT ZUSAMMENSTELLUNG =====

    def generate_full_report(self) -> Dict:
        """
        Vollständigen Report B mit allen Daten und Visualisierungen generieren

        Returns:
            Dictionary mit allen Report-Elementen
        """
        return {
            "title": "Report B - Bewegungsprotokoll & Lagerverlauf",
            "generated_at": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "movement_summary": self.get_movement_summary(),
            "inventory_statistics": self.get_inventory_statistics(),
            "category_statistics": self.get_category_statistics(),
            "movement_details": self.get_movement_details(limit=50),
            "movements_by_product": self.get_movements_by_product(),
            "charts": {
                "movement_timeline": self.generate_movement_chart(),
                "movement_types": self.generate_movement_type_chart(),
                "inventory_value": self.generate_inventory_value_chart(),
                "warehouse_vs_shop": self.generate_warehouse_vs_shop_chart(),
                "movement_quantity": self.generate_movement_quantity_chart(),
            },
        }
