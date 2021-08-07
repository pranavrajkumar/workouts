import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL(os.getenv("DATABASE_URL"))

@app.route("/")
@login_required
def index():
    """Show workouts created"""
    rows=db.execute("SELECT name, musclegroup, exercise1, reps1, exercise2, reps2, exercise3, reps3, exercise4, reps4, exercise5, reps5 FROM workouts WHERE user_id=:user_id GROUP BY name", user_id=session["user_id"])

    if not rows:
        return apology("U have no workouts, Use the create tab to create one", 200)

    workouts=[]
    a=""

    for row in rows:
        workouts.append({
            "name" : row["name"],
            "musclegroup" : row["musclegroup"],
            "exercise1" : row["exercise1"],
            "reps1" : row["reps1"],
            "exercise2" : row["exercise2"],
            "reps2" : row["reps2"],
            "exercise3" : row["exercise3"],
            "reps3" : row["reps3"],
            "exercise4" : row["exercise4"],
            "reps4" : row["reps4"],
            "exercise5" : row["exercise5"],
            "reps5" : row["reps5"]
        })

    return render_template ("index.html", workouts=workouts, a=a)

@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create workout"""
    if request.method == "POST":
        if not request.form.get("name"):
            return apology("must provide name of workout", 400)

        if not request.form.get("musclegroup"):
            return apology("must provide name of musclegroup", 400)

        if not request.form.get("exercise1"):
            return apology("must provide atleast one exercise", 400)

        if not request.form.get("reps1"):
            return apology("must provide atleast one rep", 400)

        name = request.form.get("name")
        musclegroup = request.form.get("musclegroup")
        exercise1 = request.form.get("exercise1")
        reps1 = request.form.get("reps1")
        exercise2 = request.form.get("exercise2")
        reps2 = request.form.get("reps2")
        exercise3 = request.form.get("exercise3")
        reps3 = request.form.get("reps3")
        exercise4 = request.form.get("exercise4")
        reps4 = request.form.get("reps4")
        exercise5 = request.form.get("exercise5")
        reps5 = request.form.get("reps5")


        db.execute("INSERT INTO workouts(user_id, name, musclegroup, exercise1, reps1, exercise2, reps2, exercise3, reps3, exercise4, reps4, exercise5, reps5) VALUES (:user_id, :name, :musclegroup, :exercise1, :reps1, :exercise2, :reps2, :exercise3, :reps3, :exercise4, :reps4, :exercise5, :reps5)", user_id=session["user_id"], name=name, musclegroup=musclegroup, exercise1 = exercise1, reps1 = reps1, exercise2 = exercise2, reps2=reps2, exercise3 = exercise3, reps3 = reps3, exercise4 = exercise4, reps4= reps4, exercise5 = exercise5, reps5=reps5)
        return redirect("/")

    else:
        return render_template("create.html")

@app.route("/history")
@login_required
def history():
    """Show history of workouts"""
    rows=db.execute("SELECT name, time FROM history WHERE user_id=:user_id ORDER BY time DESC", user_id=session["user_id"])

    historys=[]

    for row in rows:
        historys.append({
            "name": row["name"],
            "time": row["time"]
        })
    return render_template("history.html", historys=historys)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/do", methods=["GET", "POST"])
@login_required
def do():
    """Do a workout"""
    if request.method == "POST":
        if not request.form.get("name"):
            return apology("must provide name of workout", 403)

        name = request.form.get("name")

        rows = db.execute("SELECT name, exercise1, reps1, exercise2, reps2, exercise3, reps3, exercise4, reps4, exercise5, reps5 FROM workouts WHERE user_id=:user_id", user_id=session["user_id"])

        exercises=[]
        a=""
        for row in rows:
            if name == row["name"]:
                exercises.append({
                    "name" : row["name"],
                    "exercise1" : row["exercise1"],
                    "reps1" : row["reps1"],
                    "exercise2" : row["exercise2"],
                    "reps2" : row["reps2"],
                    "exercise3" : row["exercise3"],
                    "reps3" : row["reps3"],
                    "exercise4" : row["exercise4"],
                    "reps4" : row["reps4"],
                    "exercise5" : row["exercise5"],
                    "reps5" : row["reps5"]
                    })

        db.execute("INSERT INTO history (user_id, name) VALUES(:user_id, :name)", user_id=session["user_id"], name=request.form.get("name"))

        return render_template ("exercise.html", exercises=exercises, a=a)

    else:
        rows = db.execute("SELECT name FROM workouts WHERE user_id=:user_id", user_id=session["user_id"])
        names=[]
        for row in rows:
            names.append({"name": row["name"]})
        return render_template("do.html", names=names)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 400)

        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)

        elif (request.form.get("confirmation") != request.form.get("password")):
            return apology("password and confirmation does not match", 400)

        elif len(request.form.get("password"))<6:
            return apology("password too short", 403)

        password_hash = generate_password_hash(request.form.get("password"))

        try:
            test = db.execute("INSERT INTO users (username,hash) VALUES(?, ?)", request.form.get("username"),password_hash)
            return redirect("/")
        except ValueError:
            return apology("Username already exists", 400)

    else:
        return render_template("register.html")

@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    """Delete a workout"""
    if request.method == "POST":
        if not request.form.get("name"):
            return apology("Enter name of workout", 400)


        db.execute("DELETE FROM workouts WHERE user_id=:user_id AND name =:name", user_id=session["user_id"], name = request.form.get("name"))
        return redirect("/")

    else:
        rows = db.execute("SELECT name FROM workouts WHERE user_id=:user_id", user_id=session["user_id"])
        names=[]
        for row in rows:
            names.append({"name": row["name"]})

        return render_template("delete.html", names=names)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
