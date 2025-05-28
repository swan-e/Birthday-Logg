import functools

from quart import Blueprint, request, jsonify, session, g, render_template

from werkzeug.security import check_password_hash, generate_password_hash

from project_folder.db import get_db

import asyncpg

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
async def register():
    if request.method == 'GET':
        # Serve the registration form HTML
        return await render_template('auth/register.html')

    # Otherwise POST method:
    data = await request.get_json()
    username = data.get('username')
    password = data.get('password')

    error = None
    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is required.'

    if error:
        return jsonify({'success': False, 'error': error}), 400

    try:
        conn = await get_db()
        await conn.execute(
            "INSERT INTO logg.users (username, password) VALUES ($1, $2)",
            username,
            generate_password_hash(password)
        )
    except asyncpg.UniqueViolation:
        return jsonify({'success': False, 'error': f"User {username} already exists."}), 409
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

    return jsonify({'success': True, 'message': 'User registered successfully.'})

@bp.route('/login', methods=['GET', 'POST'])
async def login():
    if request.method == 'GET':
        return await render_template('auth/login.html')

    data = await request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password required.'}), 400

    conn = await get_db()
    user = await conn.fetchrow(
        "SELECT id, username, password FROM logg.users WHERE username = $1",
        username
    )

    if user is None:
        return jsonify({'success': False, 'error': 'Incorrect username.'}), 401
    if not check_password_hash(user['password'], password):
        return jsonify({'success': False, 'error': 'Incorrect password.'}), 401

    session.clear()
    session['user_id'] = user['id']

    return jsonify({'success': True, 'message': 'Login successful.'})

@bp.before_app_request
async def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.users = None
    else:
        conn = await get_db()
        user = await conn.fetchrow(
            "SELECT * FROM logg.users WHERE id = $1",
            user_id
        )
        g.user = user


@bp.route('/logout')
async def logout():
    session.clear()
    return await render_template('intro.html')

def login_required(view):
    @functools.wraps(view)
    async def wrapped_view(*args, **kwargs):
        if g.user is None:
            return jsonify({'success': False, 'error': 'Authentication required.'}), 401
        return await view(*args, **kwargs)
    return wrapped_view