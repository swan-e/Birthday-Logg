from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from project_folder.auth import login_required
from project_folder.db import get_db, pool

import psycopg
from psycopg.rows import dict_row

bp = Blueprint('bday', __name__)

@bp.route('/', methods=('GET', 'POST'))
def intro():
    return render_template('intro.html')

@bp.route('/home', methods = ('GET', 'POST'))
@login_required
def index():
    conn = get_db()
    print(id(conn))

    tab = request.args.get('tab') or request.form.get('tab')

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        birthday = int(request.form['birthdate[day]'])
        birthmonth = int(request.form['birthdate[month]'])
        birthyear = int(request.form['birthdate[year]'])

        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    'INSERT INTO logg.birthdays (title, body, birthday, birthmonth, birthyear, author_id)'
                    ' VALUES (%s, %s, %s, %s, %s, %s)',
                    (title, body, birthday, birthmonth, birthyear, g.user['id'])
                )
                conn.commit()
            flash('Post created successfully!')
            return redirect(url_for('bday.index', tab=tab))

    month_map = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr': 4,
        'may': 5,
        'jun': 6,
        'jul': 7,
        'aug': 8,
        'sep': 9,
        'oct': 10,
        'nov': 11,
        'dec': 12
    }

    birthmonth = month_map.get(tab.lower()) if tab else None

    query = '''
        SELECT p.id, title, body, birthday, birthmonth, birthyear, created, author_id, username
        FROM logg.birthdays p
        JOIN logg.users u ON p.author_id = u.id
    '''

    params = []

    if birthmonth:
        query += ' WHERE birthmonth = %s'
        params.append(birthmonth)
    query += ' ORDER BY created DESC'

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, params)
        birthdays = cur.fetchall()

    return render_template('bday/index.html', birthdays=birthdays, tab=tab)

def get_birthday(id, check_author=True):
    conn = get_db()
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            'SELECT p.id, title, body, birthday, birthmonth, birthyear, created, author_id, username '
            'FROM logg.birthdays p JOIN logg.users u ON p.author_id = u.id '
            'WHERE p.id = %s',
            (id,)
        )
        birthdays = cur.fetchone()

    if birthdays is None:
        abort(404, f"Birthday id {id} doesn't exist.")

    if check_author and birthdays['author_id'] != g.user['id']:
        abort(403)

    return birthdays


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    birthdays = get_birthday(id)
    tab = request.args.get('tab') or request.form.get('tab')

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        birthday = int(request.form['birthdate[day]'])
        birthmonth = int(request.form['birthdate[month]'])
        birthyear = int(request.form['birthdate[year]'])
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            conn = get_db()
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    'UPDATE logg.birthdays SET title = %s, body = %s, birthday = %s, birthmonth = %s, birthyear = %s'
                    ' WHERE id = %s',
                    (title, body, birthday, birthmonth, birthyear, id)
                )
                conn.commit()
            return redirect(url_for('bday.index', tab=tab))

    return render_template('bday/update.html', birthdays=birthdays, tab=tab)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_birthday(id)
    conn = get_db()
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute('DELETE FROM logg.birthdays WHERE id = %s', (id,))
        conn.commit()
    return redirect(url_for('bday.index'))