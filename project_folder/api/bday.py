from quart import Blueprint, request, jsonify, session, g, render_template

from werkzeug.exceptions import abort

from project_folder.api.auth import login_required
from project_folder.db import get_db, pool

import asyncpg

bp = Blueprint('bday', __name__)

@bp.route('/', methods=('GET',))
async def intro():
    return await render_template('intro.html')

@bp.route('/home', methods=['GET', 'POST'])
@login_required
async def index():
    #print("Endpoint /home accessed with method:", request.method)
    if request.method == 'POST':
        data = await request.get_json()
        print('Received POST data:', data)
        if data is None:
            return jsonify({'success': False, 'error': 'No JSON payload received'}), 400
        title = data.get('title')
        body = data.get('body')
        birthday = int(data.get('birthdate', {}).get('day', 0))
        birthmonth = int(data.get('birthdate', {}).get('month', 0))
        birthyear = int(data.get('birthdate', {}).get('year', 0))
        tab = data.get('tab')

        error = None

        if not title:
            error = 'Title is required.'
        if not birthday or not birthmonth or not birthyear:
            error = 'Complete birth date is required.'

        if error:
            return jsonify({'success': False, 'error': error}), 400

        try:
            conn = await get_db()
            await conn.execute(
                'INSERT INTO logg.birthdays (title, body, birthday, birthmonth, birthyear, author_id) '
                'VALUES ($1, $2, $3, $4, $5, $6)',
                title, body, birthday, birthmonth, birthyear, g.user['id']
            )

            print(f'Successfully inserted birthday: {title}')
            return jsonify({'success': True, 'message': 'Birthday created successfully!', 'redirect': f"/home?tab={tab}"})

        except Exception as e:
            print(f'Database error: {str(e)}')
            return jsonify({'success': False, 'error': f'Database error: {str(e)}'}), 500

    # For GET requests: render the template as usual
    tab = request.args.get('tab', 'all')
    return await render_template('base.html', tab=tab)

@bp.route('/api/birthdays')
@login_required
async def api_birthdays():
    conn = await get_db()
    user_id = g.user['id']
    tab = request.args.get('tab', 'all').lower()

    month_map = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    birthmonth = month_map.get(tab) if tab != 'all' else None

    query = '''
        SELECT p.id, title, body, birthday, birthmonth, birthyear, created, author_id, username
        FROM logg.birthdays p
        JOIN logg.users u ON p.author_id = u.id
        WHERE p.author_id = $1
    '''
    params = [user_id]
    if birthmonth:
        query += ' WHERE birthmonth = $1'
        params.append(birthmonth)
    query += ' ORDER BY created DESC'

    birthdays = await conn.fetch(query, *params)

    # Convert records to dicts (assuming `birthdays` is a list of asyncpg records)
    result = [dict(b) for b in birthdays]

    return jsonify(result)

async def get_birthday(id, check_author=True):
    conn = await get_db()

    birthdays = await conn.fetchrow(
        '''
        SELECT p.id, title, body, birthday, birthmonth, birthyear, created, author_id, username
        FROM logg.birthdays p
        JOIN logg.users u ON p.author_id = u.id
        WHERE p.id = $1
        ''',
        id
    )

    if birthdays is None:
        abort(404, f"Birthday id {id} doesn't exist.")

    if check_author and birthdays['author_id'] != g.user['id']:
        abort(403)

    return birthdays


@bp.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
async def update(id):
    print(f"Update route hit with id: {id}")
    birthdays = await get_birthday(id)
    conn = await get_db()
    tab = request.args.get('tab')

    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = await request.get_json()
            title = data.get('title')
            body = data.get('body')
            birthday = int(data.get('birthdate', {}).get('day', 0))
            birthmonth = int(data.get('birthdate', {}).get('month', 0))
            birthyear = int(data.get('birthdate', {}).get('year', 0))
        else:
            form = await request.form
            title = form['title']
            body = form['body']
            birthday = int(form['birthdate[day]'])
            birthmonth = int(form['birthdate[month]'])
            birthyear = int(form['birthdate[year]'])

        error = None

        if not title:
            error = 'Title is required.'

        if error:
            return jsonify({'success': False, 'error': error}), 400


        await conn.execute(
            '''
            UPDATE logg.birthdays
            SET title = $1, body = $2, birthday = $3, birthmonth = $4, birthyear = $5
            WHERE id = $6
            ''',
            title, body, birthday, birthmonth, birthyear, id
        )
    
        return jsonify({'success': True, 'message': 'Birthday updated successfully.', 'redirect': f'/home?tab={tab}'})

    return await render_template('bday/update.html', birthdays=birthdays, tab=tab)

@bp.route('/delete/<int:id>', methods=('POST',))
@login_required
async def delete(id):
    await get_birthday(id)
    conn = await get_db()

    try:
        await conn.execute(
            'DELETE FROM logg.birthdays WHERE id = $1',
            id
        )
        return jsonify({'success': True, 'message': 'Birthday deleted successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500