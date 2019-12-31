import hashlib
import uuid

from flask import Flask, render_template, request, redirect, url_for, make_response
from models import User, Contact, db

app = Flask(__name__)
db.create_all()  # create new tables in database


@app.route("/")  # CONTROLLER
def index():
    session_token = request.cookies.get("session_token")

    if session_token:
        # get user from the database based on email address
        user = db.query(User).filter_by(session_token=session_token).first()

    else:
        user = None

    return render_template("index.html", user=user)  # VIEW


@app.route("/about")  # CONTROLLER
def about():
    return render_template("index.html")  # VIEW


@app.route("/community")  # CONTROLLER
def community():
    return render_template("community.html")  # VIEW


@app.route("/discover")  # CONTROLLER
def discover():
    return render_template("discover.html")  # VIEW


@app.route("/contact", methods=["GET", "POST"])  # CONTROLLER
def contact():
    if request.method == "GET":
        user_name = request.cookies.get("user_name")
        print(user_name)

        return render_template("contact.html", name=user_name)
    elif request.method == "POST":
        contact_name = request.form.get("contact-name")
        contact_email = request.form.get("contact-email")
        contact_message = request.form.get("contact-message")

        print(contact_name)
        print(contact_email)
        print(contact_message)

        if contact_name:
            contact = Contact(name=contact_name, email=contact_email, message=contact_message)

            db.session.add(contact)
            db.session.commit()

        response = make_response(render_template("success.html"))
        response.set_cookie("user_name", "contact_name")

        return response  # VIEW


@app.route("/success")  # CONTROLLER
def success():
    return render_template("success.html")


@app.route("/profile", methods=["GET"])  # CONTROLLER
def profile():
    session_token = request.cookies.get("session_token")

    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()

    else:
        user = None

    return render_template("profile.html", user=user)  # VIEW


@app.route("/login", methods=["POST"])  # CONTROLLER
def login():
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    password = request.form.get("user-password")

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    user = db.query(User).filter_by(email=email).first()

    if not user:
        user = User(name=name, email=email, password=hashed_password)

    # save user into database
    db.add(user)
    db.commit()

    if hashed_password != user.password:
        return "Wrong Password. Try Again."
    elif hashed_password == user.password:
        session_token = str(uuid.uuid4())

        user.session_token = session_token
        db.add(user)
        db.commit()

        response = make_response(redirect(url_for('profile')))
        response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')

        return response


if __name__ == '__main__':
    app.run(debug=True)
