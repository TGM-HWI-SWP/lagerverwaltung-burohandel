from .main import create_app

# allow starting the web server with “python -m src.ui”
if __name__ == "__main__":
    # create and run the flask app directly
    create_app().run(debug=True)
