from datetime import datetime

import click

from quart import current_app, g
import asyncpg

pool = None

# adding connection pooling
async def init_db_pool():
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(dsn=current_app.config["SUPABASE_DB_URL"], min_size=1, max_size=10)

async def get_db():
    if 'db' not in g:
        g.db = await pool.acquire()
        await g.db.execute('SET search_path TO logg')
    return g.db

async def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        await pool.release(db)

def init_app(app):
    @app.before_serving
    async def setup_pool():
        await init_db_pool()

    @app.after_serving
    async def shutdown_pool():
        global pool
        if pool is not None:
            await pool.close()

    app.teardown_appcontext(close_db)