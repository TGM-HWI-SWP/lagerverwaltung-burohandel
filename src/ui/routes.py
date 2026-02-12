from flask import render_template, request, redirect, url_for, flash
from .fake_data import list_products


def register_routes(app):

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/shop")
    def shop():
        products = list_products()
        return render_template("shop.html", products=products)

    @app.route("/lager")
    def lager():
        products = list_products()
        return render_template("lager.html", products=products)

    @app.route("/bestellung", methods=["GET", "POST"])
    def bestellung():
        products = list_products()

        if request.method == "POST":
            product_id = request.form.get("product_id")
            amount = request.form.get("amount")

            # GUI-only: wir speichern nichts, nur Validierung + Meldung
            try:
                amount_int = int(amount)
                if amount_int <= 0:
                    raise ValueError
            except Exception:
                flash("Bitte eine gültige Anzahl > 0 eingeben.", "error")
                return redirect(url_for("bestellung"))

            flash("Bestellung wurde abgeschickt (GUI-Demo).", "success")
            return redirect(url_for("shop"))

        return render_template("bestellung.html", products=products)

    @app.route("/transfer_to_shop", methods=["POST"])
    def transfer_to_shop():
        product_id = request.form.get("product_id")
        amount = request.form.get("amount")

        # GUI-only: keine echte Anpassung, nur Demo + Validierung
        try:
            amount_int = int(amount)
            if amount_int <= 0:
                raise ValueError
        except Exception:
            flash("Bitte eine gültige Anzahl > 0 eingeben.", "error")
            return redirect(url_for("lager"))

        flash("Transfer wurde abgeschickt (GUI-Demo).", "success")
        return redirect(url_for("lager"))
