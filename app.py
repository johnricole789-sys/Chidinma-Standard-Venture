from flask import Flask
from config import Config
from extensions import db
import os


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    with app.app_context():
        import models
        db.create_all()

    from routes import main
    app.register_blueprint(main)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)