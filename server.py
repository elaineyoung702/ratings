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
    user_obj = db.session.query(User).filter(User.email==email).one()

    if password == user_obj.password:
        session['user_email'] = email
        session['user_password'] = password
        session['user_id'] = user_obj.user_id

        flash('Login successful!')

        return redirect(f"/users/{user_obj.user_id}")
    else:
        flash('Incorrect email or password.')

    
@app.route('/logout')
def log_out():
    """Removing user session data at logout."""
    
    session.clear()

    return redirect("/")


@app.route('/movies')
def show_movie_list():
    """Display list of movies."""

    movies = Movie.query.all()

    return render_template('movie_list.html', movies=movies)


@app.route('/movies/<movie_id>')
def show_movie_page(movie_id):
    """Show user's page."""

    movie = Movie.query.get(movie_id)
    user = None

    if 'user_id' in session:
        user = User.query.get(session['user_id'])

    return render_template('movie_page.html', movie=movie, user=user)


@app.route('/rate-movie', methods=['POST'])
def rate_movie():
    """Add rating to ratings table."""

    user_id = session['user_id']
    user = User.query.get(user_id)
    score = request.form.get("movie_rating")
    movie_id = request.form.get("movie_id")
    movie = Movie.query.get(movie_id)

    # if user has not rated movie, create new rating
    if movie not in user.movies:
        rating = Rating(movie_id=movie_id, user_id=user_id, score=score)
    # if user has rated movie, update old rating
    else:
        rating = db.session.query(Rating) \
            .filter(Rating.movie_id==movie_id, Rating.user_id==user_id).one()
        rating.score = score

    db.session.add(rating)
    db.session.commit()

    flash('Rated successfully!')

    return redirect(f'/movies/{movie_id}')


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
