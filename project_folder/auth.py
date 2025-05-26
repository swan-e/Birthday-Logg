import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from project_folder.db import get_db

import psycopg
from psycopg.rows import dict_row

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET','POST'))
# this route is connected to the register view function
def register():
    # when user submits the form 
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        print(id(conn))

        error = None

        # non empty validation
        if not username:
            error = 'Username is reqired.'
        elif not password:
            error = 'Password is required.'
    
        if error is None:
            try:
                # this is a standard SQL query that inserts the tuple of 
                # username and password into the database
                # WARNING: password should never be stored in the database directly
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(
                        "INSERT INTO logg.users (username, password) VALUES (%s, %s)",
                        (username, generate_password_hash(password)),
                    )
                    conn.commit()
            except conn.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
            
        flash(error)

    # this is the initial html template that is rendered for this page
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        print(id(conn))
        error = None

        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute('SELECT username, password, id FROM logg.users WHERE username = %s', (username,))
            user = cur.fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('bday.index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.users = None
    else:
        conn = get_db()
        print(id(conn))
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute('SELECT * FROM logg.users WHERE id = %s', (user_id,))
            g.user = cur.fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('bday.intro'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view