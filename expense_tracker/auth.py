import functools
from flask import Blueprint
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import flash


bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].title()
        if username.isspace():
            username = 'Guest'
        username = username.strip()
        session.clear()
        session['username'] = username
        g.user = username
        return redirect(url_for('expense.home'))

    return render_template('login.html')


@bp.route('/logout')
def logout():
    session.clear()
    flash('You were successfully logged out')
    return redirect(url_for('auth.login'))


@bp.before_app_request
def load_logged_in_user():
    username = session.get('username')

    if username is None:
        g.user = None
    else:
        g.user = username


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
