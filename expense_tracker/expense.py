from flask import Blueprint
from flask import render_template
from flask import g
from flask import session
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from expense_tracker.db import get_db
from expense_tracker.auth import login_required
from datetime import date


bp = Blueprint('expense', __name__, url_prefix='/expense-tracker')

@bp.route('/')
@login_required
def home():
    today = date.today()
    months = {}
    years = {}

    for option in range(1, 13):
        months[option] = f'{option:02d}'

    max_year = today.strftime('%Y')

    for option in range(int(max_year), 2014, -1):
        years[option] = str(option)

    month = request.args.get('month')
    year = request.args.get('year')

    if month is None:
        month = today.strftime('%m')
        year = max_year
        month_year = month + '-' + year
    else:
        month_year = month + '-' + year

    user = g.user
    db = get_db()
    results = db.execute('''SELECT id, expense_date, category, amount
                        FROM expense
                        WHERE username = ? AND
                        strftime('%m-%Y', expense_date) = ?
                        ORDER BY expense_date''', (user, month_year)
                        )
    total = db.execute('''SELECT SUM(amount)
                        FROM expense
                        WHERE username = ? AND
                        strftime('%m-%Y', expense_date) = ?''',
                        (user, month_year)
                        ).fetchone()[0]

    by_category = db.execute('''SELECT category, SUM(amount) as total
                            FROM expense
                            WHERE username = ? AND
                            strftime('%m-%Y', expense_date) = ?
                            GROUP BY category
                            ORDER BY total DESC''', (user, month_year)
                            )

    return render_template(
        'summary.html', months=months, years=years, date=month_year,
        results=results, total=total, by_category=by_category
        )


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category'].title().strip()
        if not category or category.isspace():
            category = 'Undefined'
        amount = request.form['amount']
        db = get_db()
        db.execute(
            'INSERT INTO expense (username, expense_date, category, amount)'
            ' VALUES (?, ?, ?, ?)',
            (g.user, date, category, amount)
        )
        db.commit()
        flash('Expense added')
        return redirect(url_for('expense.add'))
    return render_template('add.html')


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    user = g.user
    db = get_db()
    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category'].title().strip()
        if not category or category.isspace():
            category = 'Undefined'
        amount = request.form['amount']
        db.execute(
            '''UPDATE expense SET expense_date = ?, category = ?, amount =?
            WHERE id = ?''', (date, category, amount, id)
        )
        db.commit()
        flash('Changes saved')
        return redirect(url_for('expense.home'))

    record = (db.execute('''SELECT id, expense_date, category, amount
                        FROM expense
                        WHERE username = ? AND id = ?
                        ORDER BY expense_date''', (user, id)
                        )
                        .fetchone())
    return render_template('edit.html', record=record, id=id)
