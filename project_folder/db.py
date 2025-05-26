import psycopg2
from datetime import datetime

import click
import psycopg

from flask import current_app, g
from psycopg_pool import ConnectionPool

pool = None

# adding connection pooling
def init_app(app):
    global pool
    pool = ConnectionPool(conninfo=app.config['SUPABASE_DB_URL'], min_size=1, max_size=10)
    app.teardown_appcontext(close_db)

def get_db():
    if 'db' not in g:
        # flask --app project_folder init-db 
        # ^ the above is how to start up the local db
        g.db = pool.getconn()
        with g.db.cursor() as cur:
            cur.execute('SET search_path TO logg')
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        pool.putconn(db)