"""
!                                                   ----- KeyFinder -----
TODO: Ideas and Suggestions:
* There's a problem with the timer module.
    -> Timer object can be created using Threads but after the time limit is finished, we need to send 
    notifications every hour.
    
"""

from flask import Flask, render_template, session, request, redirect, url_for, flash, jsonify
from functools import wraps
from datetime import datetime, timedelta
import pymongo
import requests
from bson.objectid import ObjectId
from passlib.hash import sha256_crypt

import time #? This is a test
import threading #? This is a test
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

#! Timeout
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)

#! Telegram Notification
#TODO=> Bot token and ChatID has to come from database
def telegramNotificationSend(botMessage, botToken, botChatID):
    bot_token = botToken
    bot_chatID = botChatID
    sendMessage = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + \
                '&parse_mode=Markdown&text=' + botMessage

    requests.get(sendMessage)

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
@app.route("/dashboard")
@login_required
def dashboard():
    last4Logs = []
    #last4LogsTime = []
    data = ['test1','test2','test3','test4']
    
    for i in logs.find().sort([('$natural', -1)]).limit(4):
        last4Logs.append(i)

    #for post in logs.find({"fullname": "Waasiq"}):
    #    print(post['givenTime'])

    if last4Logs:
        return render_template('dashboard.html', last4Logs=last4Logs, data=data)
    else:
        flash("Database connection error.", "danger")
        return render_template('dashboard.html')
        
#! Timer Object
# @app.route("/updateTimer", methods=['POST'])
# def updateTimer():
#     hours = 5.0 #? This is the time(seconds) in float type. This part will change depending on type of clothes and coin count.
#         # hours = hours * 3600 #? Seconds to hours
#     timer = threading.Timer(hours, telegramNotification)
#     timer.start() 

#     return jsonify(render_template("timer.html", countdownTest=timer))

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
            'creationDate' : datetime.now(),
            'givenTime': request.form.get('timeGiven')

            #! Insert timer here after calculation w.r.t to the coins and 
            #! color type.
        }
        logs.insert_one(resident)
        flash("Resident saved, timer has been started.","warning")

        #TODO -> Timer object will come here.
        #* Using threads ==> kinda worked, more tests required
        # hours = 5.0 #? This is the time(seconds) in float type. This part will change depending on type of clothes and coin count.
        # hours = hours * 3600 #? Seconds to hours
        # timer = threading.Timer(hours, telegramNotification)
        # timer.start() 
        # print("Wait for it, wait for it........")

        #TODO -> Telegram Notifications testing
        #* After saving a customer, a notification will be sent
        checkCustomer = telegramInfo.find_one({"customerName":resident['fullname']})
    
        if checkCustomer:
            telegramNotificationSend(f"***{resident['fullname']}***, your timer has been started. Current date and time: `{datetime.now()}`",
                                     botToken=checkCustomer['token'], botChatID=checkCustomer['chatID'])

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
    
    # telegramNotificationSend("Wazzup")