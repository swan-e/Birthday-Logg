import os 
from datetime import datetime, timezone

from quart import Quart
from dotenv import load_dotenv


def create_app(test_config=None):
    app = Quart(__name__, instance_relative_config=True)

    app.config['DEBUG'] = True
    app.config['ENV'] = 'development'

    @app.context_processor
    def inject_now():
        return {'now': datetime.now(timezone.utc)}

    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),
        SUPABASE_DB_URL=os.getenv('SUPABASE_DB_URL')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from . import db
    db.init_app(app)

    from .api import auth
    app.register_blueprint(auth.bp)

    from .api import bday
    app.register_blueprint(bday.bp)
    app.add_url_rule('/', endpoint='index')
    
    return app