from datetime import datetime

from flask import Flask, flash, render_template, redirect, request, url_for
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)

from models import User, Business, Event, Post, Friendship, Attendance, db
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.config.from_object('config')  # Load configuration from config.py

# TODO: Add login
login_manager = LoginManager(app)
login_manager.login_view = "login_page"

with app.app_context():
    db.init_app(app)
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")

@app.route("/register_action", methods=["POST"])
def register_action():
    username = request.form["username"]
    password = request.form["password"]
    if User.query.filter_by(name=username).first():
        flash(f"The username '{username}' is already taken")
        return redirect(url_for("register_page"))

    user = User(name=username, password=password)
    db.session.add(user)
    db.session.commit()

    login_user(user)
    flash(f"Welcome {username}!")
    return redirect(url_for("index"))

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_action():
    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(name=username).first()
    if not user:
        flash(f"No such user '{username}'")
        return redirect(url_for("login_page"))
    if password != user.password:
        flash(f"Invalid password for the user '{username}'")
        return redirect(url_for("login_page"))

    login_user(user)
    flash(f"Welcome back, {username}!")
    return redirect(url_for("index"))

@app.route("/logout", methods=["GET"])
@login_required
def logout_page():
    return render_template("logout.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout_action():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("index"))

@app.route('/')
@login_required
def index():
    businesses = Business.query.outerjoin(Event).all()
    return render_template('index.html', businesses=businesses)


@app.route('/create_business', methods=['GET', 'POST'])
@login_required
def create_business():
    if request.method == 'POST':
        name = request.form['name']
        business_type = request.form['business_type']
        address = request.form['address']
        menu = request.form['menu']
        promotions = request.form['promotions']
        business = Business(
            name=name,
            business_type=business_type,
            address=address,
            menu=menu,
            promotions=promotions,
        )
        db.session.add(business)
        db.session.commit()

        # set the current user's managed business to the new business
        current_user.managed_business = business
        db.session.add(current_user)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('create_business.html')


@app.route('/edit_business/<int:business_id>', methods=['GET', 'POST'])
@login_required
def edit_business(business_id):
    business = Business.query.get(business_id)
    if request.method == 'POST':
        business.name = request.form['name']
        business.business_type = request.form['business_type']
        business.address = request.form['address']
        business.menu = request.form['menu']
        business.promotions = request.form['promotions']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_business.html', business=business)


@app.route('/delete_business/<int:business_id>', methods=['GET', 'POST'])
@login_required
def delete_business(business_id):
    business = Business.query.get(business_id)
    if request.method == 'POST':
        db.session.delete(business)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('delete_business.html', business=business)

@app.route('/create_event_page')
def create_event_page():
    businesses = Business.query.all()
    return render_template('create_event.html',businesses=businesses)

@app.route('/create_event_action', methods=['POST'])
def create_event_action():
    business_id = request.form['business_name']
    event_name = request.form['event_name']
    event_type = request.form['event_type']
    event_description = request.form['event_description']
    event_start_time = datetime.strptime(request.form['event_start_time'], '%Y-%m-%d')
    event_end_time = datetime.strptime(request.form['event_end_time'], '%Y-%m-%d')
    business = Business.query.get(business_id)
    business.events.append(Event(
        name=event_name,
        event_type=event_type,
        start_time=event_start_time,
        end_time=event_end_time,
    ))
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)