import os 
from datetime import datetime, timezone

from flask import Flask
from dotenv import load_dotenv


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    @app.context_processor
    def inject_now():
        return {'now': datetime.now(timezone.utc)}

    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),
        DATABASE=os.path.join(app.instance_path, 'logg.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello World!'
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import bday
    app.register_blueprint(bday.bp)
    app.add_url_rule('/', endpoint='index')
    
    return app