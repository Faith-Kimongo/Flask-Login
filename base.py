from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
# from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name =name
        self.email = email

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/view")
def view():
    return render_template("view.html", values=users.query.all())

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"]= user

        found_user = users.query.filter_by(name=user).first()
        if found_user:
            session["email"] = found_user.email
        else:
            usr = users(user, "")
            db.session.add(usr)          
            db.session.commit()


        flash("Login succesful")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already logged in")
            return redirect(url_for("user"))
        flash("You are not logged in!")
        return render_template("login.html")


@app.route("/user", methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        flash("Already Logged in!")
        user = session["user"]

        if request.method == "POST":
            email = request.form["email"]
            session["email"] =  email
            found_user = users.query.filter_by(name=user).first()
            found_user.email = email
            db.session.commit()
            flash("Email was saved.")
        else:
            if "email" in session:
                email = session["email"]

        return render_template("user.html", email=email)
    else:
        
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    flash("You have been logged out.", "info")
    # remove user and email when user logs out
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))

# @app.route("/<name>")
# def user(name):
#     return f"Hello {escape(name)}"


# @app.route("/admin")
# def admin():
#     return redirect(url_for("user", name="Admin!!"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)