from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from project_folder.auth import login_required
from project_folder.db import get_db


bp = Blueprint('bday', __name__)

@bp.route('/', methods=('GET', 'POST'))
def intro():
    return render_template('intro.html')

@bp.route('/home', methods = ('GET', 'POST'))
@login_required
def index():
    db = get_db()
    tab = request.args.get('tab') or request.form.get('tab')

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        birthday = request.form['birthdate[day]']
        birthmonth = request.form['birthdate[month]']
        birthyear = request.form['birthdate[year]']

        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db.execute(
                'INSERT INTO post (title, body, birthday, birthmonth, birthyear, author_id)'
                ' VALUES (?, ?, ?, ?, ?, ?)',
                (title, body, birthday, birthmonth, birthyear, g.user['id'])
            )
            db.commit()
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
        FROM post p
        JOIN user u ON p.author_id = u.id
    '''

    params = []

    if birthmonth:
        query += ' WHERE birthmonth = ?'
        params.append(birthmonth)
    query += ' ORDER BY created DESC'
    posts = db.execute(query, params).fetchall()

    #old query
    '''
    posts = db.execute(
        'SELECT p.id, title, body, birthday, birthmonth, birthyear, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    '''

    return render_template('bday/index.html', posts=posts, tab=tab)

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, birthday, birthmonth, birthyear, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    tab = request.args.get('tab') or request.form.get('tab')

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        birthday = request.form['birthdate[day]']
        birthmonth = request.form['birthdate[month]']
        birthyear = request.form['birthdate[year]']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?, birthday = ?, birthmonth = ?, birthyear = ?'
                ' WHERE id = ?',
                (title, body, birthday, birthmonth, birthyear, id)
            )
            db.commit()
            return redirect(url_for('bday.index', tab=tab))

    return render_template('bday/update.html', post=post, tab=tab)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('bday.index'))