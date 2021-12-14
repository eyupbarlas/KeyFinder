from flask import Flask, render_template, session, request, redirect, url_for, flash
from functools import wraps
from datetime import datetime, timedelta
import pymongo
from bson.objectid import ObjectId
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

#! User entry decorator 
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
    app.permanent_session_lifetime = timedelta(minutes=15)

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
        
        if passVerify:   
            flash("Login successful!","success")
            session["logged_in"] = True
            session["username"] = user['usernameEntry']   

            return redirect(url_for("dashboard"))
        
        else:
            flash("User doesn't exist.","danger")
            return redirect(url_for("login"))
    else:
        return render_template('login.html')

#! Dashboard page
@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == "POST":
        startPause = request.form.get('startPauseToggle')
        print(startPause)
        
        return render_template("dashboard.html", startPause=startPause)
    else:
        last2Logs = []
        for i in logs.find().sort([('$natural', -1)]).limit(2):
            last2Logs.append(i)
    
        if last2Logs:
            return render_template('dashboard.html', last2Logs=last2Logs)
        else:
            flash("Database connection error.", "danger")
            return render_template('dashboard.html')

        # return render_template('dashboard.html')
    
#! Add resident page
@app.route("/dashboard/addResident", methods=['GET', 'POST'])
@login_required
def addResident():
    if request.method == 'POST':
        resident = {
            'fullname' : request.form.get('residentFullName'),
            'roomNum' : request.form.get('residentRoomNum'),
            'laundryNum' : request.form.get('laundryRoomNum'),
            'coinCount' : request.form.get('coinCount'),
            'laundryType' : request.form.getlist('laundryType'),
            'creationDate' : datetime.now()
        }
        logs.insert_one(resident)
        flash("Resident saved, timer has been started.","warning")
        return redirect(url_for('dashboard'))
    
    return render_template('addResident.html')

#! All logs for Admin
@app.route("/allLogs")
@login_required
def allLogs():
    allTimeLogs = logs.find()
    if allTimeLogs:
        return render_template('allLogs.html', allTimeLogs=allTimeLogs)
        
    return render_template('allLogs.html')

#! Logout
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("Logout successful.","success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
    # ui.run() #? This is a test
    # x = sha256_crypt.encrypt("1234")
    # print(x)
    