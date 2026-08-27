from flask import Flask

from config import Config
from routes import main_blueprint
import models


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(main_blueprint)
    app.teardown_appcontext(models.close_db)

    models.init_db(app)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
