"""Flask Application für Lagerverwaltung"""

import os
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

from src.adapters.repository import SQLiteRepository
from src.adapters.report import ConsoleReportAdapter
from src.reports.report_b import ReportB
from src.services import WarehouseService


def create_app(db_path: str = "warehouse.db") -> Flask:
    """
    Flask App Factory

    Args:
        db_path: Pfad zur warehouse.db Datenbank

    Returns:
        Konfigurierte Flask App
    """
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent / "src" / "ui" / "templates"),
        static_folder=str(Path(__file__).parent / "src" / "ui" / "static"),
    )

    # Konfiguration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-change-in-production")
    app.config["DATABASE"] = db_path

    # Services initialisieren
    repository = SQLiteRepository(db_path=db_path)
    report_adapter = ConsoleReportAdapter()
    service = WarehouseService(repository=repository, report_adapter=report_adapter)

    # Service in App speichern für Zugriff in Routes
    app.warehouse_service = service

    # ===== ROUTES =====

    @app.route("/")
    def index():
        """Dashboard mit Statistiken"""
        stats = app.warehouse_service.get_dashboard_stats()
        return render_template("dashboard.html", stats=stats)

    @app.route("/suche", methods=["GET"])
    def suche():
        """Produktsuche"""
        query = request.args.get("q", "").strip()
        products = []
        categories = app.warehouse_service.get_product_categories()
        
        if query:
            products = app.warehouse_service.search_products(query)
        
        return render_template("suche.html", products=products, query=query, categories=categories)

    @app.route("/kategorie/<category>")
    def kategorie(category):
        """Produkte nach Kategorie filtern"""
        products = app.warehouse_service.get_products_by_category(category)
        categories = app.warehouse_service.get_product_categories()
        return render_template("kategorie.html", products=products, selected_category=category, categories=categories)

    @app.route("/lager")
    def lager():
        """Lager-Übersicht"""
        products = app.warehouse_service.get_products_with_totals()
        low_stock_count = app.warehouse_service.get_low_stock_count()
        return render_template("lager.html", products=products, low_stock_count=low_stock_count)

    @app.route("/low-stock")
    def low_stock():
        """Low Stock Dashboard - Produkte unter Minimum"""
        products = app.warehouse_service.get_low_stock_products()
        return render_template("low_stock.html", products=products)

    @app.route("/shop")
    def shop():
        """Shop-Übersicht"""
        products = app.warehouse_service.get_products_with_totals()
        return render_template("shop.html", products=products)

    @app.route("/einkauf", methods=["GET", "POST"])
    def einkauf():
        """Einkauf von Lieferanten - neue Produkte ins Lager"""
        if request.method == "POST":
            product_id = request.form.get("product_id")
            try:
                quantity = int(request.form.get("quantity", 0))
            except ValueError:
                flash("Ungültige Menge", "danger")
                return redirect(url_for("einkauf"))

            if quantity <= 0:
                flash("Menge muss größer als 0 sein", "danger")
                return redirect(url_for("einkauf"))

            reason = request.form.get("reason", "")
            success = app.warehouse_service.create_purchase(product_id, quantity, reason)

            if success:
                product = app.warehouse_service.get_product(product_id)
                flash(f"Einkauf erfolgreich: {quantity}x {product.name} ins Lager", "success")
                return redirect(url_for("index"))
            else:
                flash("Einkauf fehlgeschlagen", "danger")
                return redirect(url_for("einkauf"))

        products = app.warehouse_service.get_products_with_totals()
        return render_template("einkauf.html", products=products)

    @app.route("/transfer", methods=["GET", "POST"])
    def transfer():
        """Transfer zwischen Lager und Shop"""
        if request.method == "POST":
            product_id = request.form.get("product_id")
            quantity = int(request.form.get("quantity", 0))
            direction = request.form.get("direction")  # "to_shop" oder "to_warehouse"

            if quantity <= 0:
                flash("Menge muss größer als 0 sein", "danger")
                return redirect(url_for("transfer"))

            if direction == "to_shop":
                success = app.warehouse_service.transfer_to_shop(product_id, quantity)
                if success:
                    product = app.warehouse_service.get_product(product_id)
                    flash(f"Transfer erfolgreich: {quantity}x {product.name} zum Shop", "success")
                else:
                    flash("Transfer fehlgeschlagen - Nicht genug Bestand im Lager", "danger")
            elif direction == "to_warehouse":
                success = app.warehouse_service.transfer_to_warehouse(product_id, quantity)
                if success:
                    product = app.warehouse_service.get_product(product_id)
                    flash(f"Transfer erfolgreich: {quantity}x {product.name} zum Lager", "success")
                else:
                    flash("Transfer fehlgeschlagen - Nicht genug Bestand im Shop", "danger")
            else:
                flash("Ungültige Richtung", "danger")

            return redirect(url_for("transfer"))

        products = app.warehouse_service.get_products_with_totals()
        return render_template("transfer.html", products=products)

    @app.route("/verkauf", methods=["GET", "POST"])
    def verkauf():
        """Kundenverkauf - Produkte aus dem Shop"""
        if request.method == "POST":
            product_id = request.form.get("product_id")
            try:
                quantity = int(request.form.get("quantity", 0))
            except ValueError:
                flash("Ungültige Menge", "danger")
                return redirect(url_for("verkauf"))

            if quantity <= 0:
                flash("Menge muss größer als 0 sein", "danger")
                return redirect(url_for("verkauf"))

            reason = request.form.get("reason", "")
            success = app.warehouse_service.sell_product(product_id, quantity, reason)

            if success:
                product = app.warehouse_service.get_product(product_id)
                flash(f"Verkauf erfolgreich: {quantity}x {product.name}", "success")
                return redirect(url_for("index"))
            else:
                flash("Verkauf fehlgeschlagen - Nicht genug Bestand im Shop", "danger")
                return redirect(url_for("verkauf"))

        products = app.warehouse_service.get_products_with_totals()
        return render_template("verkauf.html", products=products)

    @app.route("/report_b")
    def report_b():
        """Report B - Bewegungsprotokoll und Lagerverlauf-Statistiken"""
        movements = app.warehouse_service.get_movements()
        products = app.warehouse_service.get_products_with_totals()
        
        report_generator = ReportB(movements, products)
        report_data = report_generator.generate_full_report()
        
        return render_template("report_b.html", report=report_data)

    @app.route("/bestellung", methods=["GET", "POST"])
    def bestellung():
        """DEPRECATED: use /verkauf instead"""
        return redirect(url_for("verkauf"))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="127.0.0.1", port=5000)
