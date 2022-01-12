"""
!                                     ----- KeyFinder -----

* Important info: Only two laundry keys are there i.e 205 and 405.
? Make a dropdown menu maybe? 
* Google Forms link for Telegram Info: https://forms.gle/kB7yUi6nb6rmpYpN9
    ! Don't forget the change the link in Terms & Conditions before launch.(Update terms and Google Form)
    ! No need to get people's chatID's and tokens. Just a group link.
"""

from flask import Flask, render_template, session, request, redirect, url_for, flash, jsonify
from functools import wraps
from datetime import datetime, timedelta
import pymongo
import requests
from bson.objectid import ObjectId
from passlib.hash import sha256_crypt
from config import BOT_TOKEN, BOT_CHATID

#! Flask app init
app = Flask(__name__)
app.secret_key = "Bzzmans_Secret"


#! MongoDB init
client = pymongo.MongoClient('localhost',27017) #TODO=> Before production stage: Localhost --> MongoDB Atlas Cloud 
db = client.KeyFinderTest1 # change collection name before launch
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

#! Timeout (15 mins)
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)

#! Telegram Notification
def telegramNotificationSend(botMessage):
    bot_token = BOT_TOKEN  
    bot_chatID = BOT_CHATID
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
            'laundryNum' : request.form.get('laundryRooms'), #TODO: Will be a dropdown.
            'coinCount' : request.form.get('coinCount'),
            'laundryType' : request.form.getlist('laundryType'),
            'creationDate' : datetime.now(),
            'givenTime': request.form.get('givenTime'),
            'loginWhoIs' : session['username']
        }
        logs.insert_one(resident)
        flash("Resident saved, timer has been started.","warning")

        #! Dropdown tests below
        print(request.form.get('laundryRooms'))

        # checkCustomer = telegramInfo.find_one({"customerName":resident['fullname']})
    
        # if checkCustomer:
        #     telegramNotificationSend(f"***{resident['fullname']}***, your laundry timer has been started. Current date and time: `{datetime.now()}`",
        #                              botToken=checkCustomer['token'], botChatID=checkCustomer['chatID'])

        # print(f"***Telegram message is sent to {resident['fullname']}.***")

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

# @app.route('/json')
# def json():
#     return render_template('process.html')

    
@app.route("/startMessage")
@login_required
def startMessage():
    print("startMessage() works.")
 
    testdata = logs.find_one(sort=[('$natural', -1)])
    currentUserName = testdata['fullname'] 
    print(currentUserName)

    telegramNotificationSend(f"***@{currentUserName}***, your timer has been started. Current date and time: `{datetime.now()}`")

    return ("nothing")

if __name__ == "__main__":
    app.run(debug=True)
    # x = sha256_crypt.encrypt("1234")
    # print(x)
    
    # telegramNotificationSend("Wazzup", botToken="5039844581:AAEJ3ZgnE3bFcljj_qduAGCCVhRC27I4k3A", botChatID="-637535626")