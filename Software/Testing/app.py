from flask import Flask, render_template, session, request, redirect, url_for, flash
from functools import wraps
from datetime import timedelta
import pymongo
from passlib.hash import sha256_crypt 
# from flaskwebgui import FlaskUI #? This is a test

#! Flask app init
app = Flask(__name__)
app.secret_key = "Bzzmans_Secret"

#? This is a test
# ui = FlaskUI(app, width=500, height=500)

#! MongoDB init
client = pymongo.MongoClient('localhost',27017)
db = client.KeyFinderTest1
users = db.users
logs = db.logs
feedbacks = db.feedbacks

#! User entry decorator (kinda default stuff except if)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("You have to login first. Unauthorised action.","danger")
            return redirect(url_for("login"))
    return decorated_function

#! Timeout
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)

# ========================================================================================

#! Index page
@app.route("/")
def index():
    return render_template("index.html")

#! About page
@app.route("/about")
def about():
    return render_template("about.html")

#! Login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user = {
            "usernameEntry" : request.form.get("usernameEntry"),
            "passwordEntry" : request.form.get("passwordEntry")
        }
        usr = users.find_one({'username': user['usernameEntry']})
        
        passVerify = sha256_crypt.verify(user['passwordEntry'],usr['password'])
   
        if passVerify is True:   
            flash("Login successful!","success")
            session["logged_in"] = True
            session["username"] = user['usernameEntry']   

            return redirect(url_for("about"))
        
        else:
            flash("User doesn't exist.","danger")
            return redirect(url_for("login"))
    else:
        return render_template('login.html')

#! Dashboard page
@app.route("/dashboard")
@login_required
def dashboard():
    allLogs = logs.find()
    if allLogs:
        return render_template('dashboard.html', allLogs=allLogs)
    
    return render_template('dashboard.html')
    

#! Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("Logout successful.","success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
    # ui.run() #? This is a test
    # x = sha256_crypt.encrypt("1234")
    # print(x)
    