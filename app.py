"""Flask Application für Lagerverwaltung"""

import os
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

from src.adapters.repository import SQLiteRepository
from src.adapters.report import ConsoleReportAdapter
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
        """Startseite"""
        return render_template("index.html")

    @app.route("/lager")
    def lager():
        """Lager-Übersicht"""
        products = app.warehouse_service.get_products_with_totals()
        return render_template("lager.html", products=products)

    @app.route("/shop")
    def shop():
        """Shop-Übersicht"""
        products = app.warehouse_service.get_products_with_totals()
        return render_template("shop.html", products=products)

    @app.route("/bestellung", methods=["GET", "POST"])
    def bestellung():
        """Bestellungsformular"""
        if request.method == "POST":
            product_id = request.form.get("product_id")
            try:
                amount = int(request.form.get("amount", 0))
            except ValueError:
                flash("Ungültige Menge", "danger")
                return redirect(url_for("bestellung"))

            if amount <= 0:
                flash("Menge muss größer als 0 sein", "danger")
                return redirect(url_for("bestellung"))

            # Bestellung ausführen
            success = app.warehouse_service.create_order(product_id, amount)

            if success:
                product = app.warehouse_service.get_product(product_id)
                flash(f"Bestellung erfolgreich: {amount}x {product.name}", "success")
                return redirect(url_for("index"))
            else:
                flash("Bestellung fehlgeschlagen - Nicht genug Bestand", "danger")
                return redirect(url_for("bestellung"))

        # GET-Request: Formular anzeigen
        products = app.warehouse_service.get_products_with_totals()
        return render_template("bestellung.html", products=products)

    @app.route("/transfer_to_shop", methods=["POST"])
    def transfer_to_shop():
        """Produkt vom Lager in den Shop transferieren"""
        product_id = request.form.get("product_id")
        try:
            amount = int(request.form.get("amount", 0))
        except ValueError:
            flash("Ungültige Menge", "danger")
            return redirect(url_for("lager"))

        if amount <= 0:
            flash("Menge muss größer als 0 sein", "danger")
            return redirect(url_for("lager"))

        # Transfer ausführen
        success = app.warehouse_service.transfer_to_shop(product_id, amount)

        if success:
            product = app.warehouse_service.get_product(product_id)
            flash(f"Transfer erfolgreich: {amount}x {product.name} zum Shop", "success")
        else:
            flash("Transfer fehlgeschlagen - Nicht genug Bestand im Lager", "danger")

        return redirect(url_for("lager"))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="127.0.0.1", port=5000)
