"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, request, redirect, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Movie, Rating


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/users')
def show_users():
    """List all users."""

    users = User.query.order_by(User.user_id.desc()).all()

    return render_template("user_list.html", users=users)


@app.route('/users/<user_id>')
def show_user_page(user_id):
    """Show user's page."""

    user = User.query.get(user_id)

    return render_template('user_page.html', user=user)


@app.route('/register', methods=["GET"])
def register_form():
    """Show registration form."""

    return render_template("register_form.html")


@app.route('/register', methods=["POST"])
def register_process():
    """Process registration form submission."""

    # get email and password from registration form
    email = request.form.get("email")
    password = request.form.get("password")

    # if user does not exist in db, create
    if (email,) not in db.session.query(User.email).all():
        user_record = User(email=email, password=password)
        db.session.add(user_record)
        db.session.commit()

    # add login info to session so we know they're logged in
    user_check = db.session.query(User).filter(User.email==email).one()

    if password == user_check.password:
        session['user_email'] = email
        session['user_password'] = password

        flash('Login successful!')

        return redirect(f"/users/{user_check.user_id}")
    else:
        flash('Incorrect email or password.')

    
@app.route('/logout')
def log_out():
    # session.clear()
    del session['user_email']
    del session['user_password']

    return redirect("/")


@app.route('/movies')
def show_movie_list():

    movies = Movie.query.all()

    return render_template('movie_list.html', movies=movies)



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
