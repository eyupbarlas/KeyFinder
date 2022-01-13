"""
!                                     ----- KeyFinder -----

* Google Forms link for Telegram Info: https://forms.gle/5udBj6vADnepoNjh8
    ! Don't forget the change the link in Terms & Conditions before launch.(Update terms and Google Form)
    ! No need to get people's chatID's and tokens. Just a group link.
        ? ChatID for group link gets updated everytime a user joins --> Careful.
"""

from flask import Flask, render_template, session, request, redirect, url_for, flash
from functools import wraps
from datetime import datetime
import pymongo
from passlib.hash import sha256_crypt
from utils import *
from config import DB_TOKEN

#! Flask app init
app = Flask(__name__)
app.secret_key = "Bzzmans_Secret"

#! MongoDB init
client = pymongo.MongoClient(DB_TOKEN) 
db = client.KeyFinder_Project
users = db.users
logs = db.logs
telegramInfo = db.telegramInfo

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

# ========================================================================================

#! Index page
@app.route("/")
def index():
    return render_template("index.html")

#! About page
@app.route("/about")
def about():
    return render_template("about.html")

#! Terms page
@app.route("/terms")
def terms():
    return render_template("terms.html")

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
@app.route("/dashboard")
@login_required
def dashboard():
    last2Logs = []
    
    for i in logs.find().sort([('$natural', -1)]).limit(2):  # Query for latest 2 records
        last2Logs.append(i)

    if last2Logs:
        return render_template('dashboard.html', last2Logs=last2Logs)
    else:
        flash("Database connection error.", "danger")
        return render_template('dashboard.html')

#! Add resident page
@app.route("/dashboard/addResident", methods=['GET', 'POST'])
@login_required
def addResident():
    if request.method == 'POST':
        resident = {
            'fullname' : request.form.get('residentFullName'),
            'roomNum' : request.form.get('residentRoomNum'),
            'laundryNum' : request.form.get('laundryRooms'), 
            'coinCount' : request.form.get('coinCount'),
            'laundryType' : request.form.getlist('laundryType'),
            'creationDate' : datetime.now(),
            'givenTime': request.form.get('givenTime'),
            'loginWhoIs' : session['username']
        }
        logs.insert_one(resident)
        flash("Resident saved, timer has been started.","warning")

        return redirect(url_for('dashboard'))
    
    return render_template('addResident.html')

#! All logs for Admin
@app.route("/allLogs")
@login_required
def allLogs():
    allTimeLogs = logs.find().sort([('$natural', -1)])
    if allTimeLogs:
        return render_template('allLogs.html', allTimeLogs=allTimeLogs)
        
    return render_template('allLogs.html')

#! Start Message for 1. Resident  
@app.route("/startMessage")
@login_required
def startMessage():
    last2logs = []
    for i in logs.find().sort([('$natural', -1)]).limit(2):
        last2logs.append(i)

    currentUserName = last2logs[0]['fullname']

    telegramNotificationSend(f"***@{currentUserName}***, your timer has been started. Current date and time: `{datetime.now()}`")

    return ("startMessage")

#! Overtime Message for 1. Resident  
@app.route("/overtimeMessage")
@login_required
def overtimeMessage():
    last2logs = []
    for i in logs.find().sort([('$natural', -1)]).limit(2):
        last2logs.append(i)

    currentUserName = last2logs[0]['fullname']

    telegramNotificationSend(f"***@{currentUserName}***, your timer has been finished and you are on overtime. Current date and time: `{datetime.now()}`")

    return ("overtimeMessage")

#! Stop Message for 1. Resident  
@app.route("/stopMessage")
@login_required
def stopMessage():
    last2logs = []
    for i in logs.find().sort([('$natural', -1)]).limit(2):
        last2logs.append(i)

    currentUserName = last2logs[0]['fullname']

    telegramNotificationSend(f"***@{currentUserName}***, your timer has been stopped. Current date and time: `{datetime.now()}`")

    return ("stopMessage")

#! Start Message for 2. Resident  
@app.route("/startMessageTwo")
@login_required
def startMessageTwo():
    last2logs = []
    for i in logs.find().sort([('$natural', -1)]).limit(2):
        last2logs.append(i)

    currentUserName = last2logs[1]['fullname']

    telegramNotificationSend(f"***@{currentUserName}***, your timer has been started. Current date and time: `{datetime.now()}`")

    return ("startMessageTwo")

#! Overtime Message for 2. Resident  
@app.route("/overtimeMessageTwo")
@login_required
def overtimeMessageTwo():
    last2logs = []
    for i in logs.find().sort([('$natural', -1)]).limit(2):
        last2logs.append(i)

    currentUserName = last2logs[1]['fullname']

    telegramNotificationSend(f"***@{currentUserName}***, your timer has been finished and you are on overtime. Current date and time: `{datetime.now()}`")

    return ("overtimeMessageTwo")

#! Stop Message for 2. Resident  
@app.route("/stopMessageTwo")
@login_required
def stopMessageTwo(): 
    last2logs = []
    for i in logs.find().sort([('$natural', -1)]).limit(2):
        last2logs.append(i)

    currentUserName = last2logs[1]['fullname']

    telegramNotificationSend(f"***@{currentUserName}***, your timer has been stopped. Current date and time: `{datetime.now()}`")

    return ("stopMessageTwo")

#! Logout
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("Logout successful.","success")
    return redirect(url_for("index"))


#! Flask run
if __name__ == "__main__":
    app.run(debug=True)
