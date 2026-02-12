from flask import Flask
from .routes import register_routes   # ✅ das ist richtig

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config["SECRET_KEY"] = "dev"

    register_routes(app)   # jetzt funktioniert das

    return app

if __name__ == "__main__":
    create_app().run(debug=True)

