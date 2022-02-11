"""
!                                     ----- KeyFinder -----

* Google Forms link for Telegram Info: https://forms.gle/emYCYLSeXpEdh8hB9
    ! No need to get people's chatID's and tokens. Just a group link.
        ? ChatID for group link gets updated everytime a user joins --> Careful.
"""
#! Importing Libraries
from flask import Flask, render_template, session, request, redirect, url_for, flash
from functools import wraps
from datetime import datetime, timedelta
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

#! User entry decorator for restricting unlogged operations
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

#! Terms page
@app.route("/terms")
def terms():
    return render_template("terms.html")

#! Login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user = {    # Getting form requests to match with database
            "usernameEntry" : request.form.get("usernameEntry"),
            "passwordEntry" : request.form.get("passwordEntry")
        }
        usr = users.find_one({'username': user['usernameEntry']}) # database query
        
        passVerify = sha256_crypt.verify(user['passwordEntry'],usr['password']) # sha256 verification
        
        if passVerify:   
            flash("Login successful!","success")
            session["logged_in"] = True  # starting session
            session["username"] = user['usernameEntry']   
            print(color.GREEN + f"Login successful. User: {session['username']}")

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
        resident = {    # Getting form requests to save data to the database
            'telegramUsername' : request.form.get('telegramUsername'),
            'roomNum' : request.form.get('residentRoomNum'),
            'laundryNum' : request.form.get('laundryRooms'), 
            'coinCount' : request.form.get('coinCount'),
            'laundryType' : request.form.getlist('laundryType'),
            'creationDate' : datetime.now(),
            'givenTime': request.form.get('givenTime'),
            'startTime' : datetime(1, 1, 1, 1, 1, 1, 1),
            'endTime' : datetime(1, 1, 1, 1, 1, 1, 1), 
            'overtimeCount' : 0,
            'startCount' : 0,
            'stopCount' : 0,
            'status' : 'Idle',
            'loginWhoIs' : session['username']
        }
        logs.insert_one(resident) # saving resident
        flash("Resident has been saved successfully.","warning")
        print(color.GREEN + "Resident saved.")
        print(color.PURPLE + f"Resident info:\n{resident}")

        return redirect(url_for('dashboard'))
    
    return render_template('addResident.html')

#! All logs for Admin
@app.route("/allLogs")
@login_required
def allLogs():
    allTimeLogs = logs.find().sort([('$natural', -1)]) # querying all logs
    if allTimeLogs:
        return render_template('allLogs.html', allTimeLogs=allTimeLogs)
        
    return render_template('allLogs.html')

#! Start Message for 1. Resident  
@app.route("/startMessage")
@login_required
def startMessage():
    last2logs = []
    for i in logs.find().sort([('$natural', -1)]).limit(2): # query of last 2 logs
        last2logs.append(i)

    currentUserName = last2logs[0]['telegramUsername'] # generating fullname from query to send Telegram notifications
    currentUserId = last2logs[0]['_id'] # getting _id for queries

    startQuery = {'_id' : currentUserId}
    startNewValues = {
        '$set':{ # setting the startTime's value with current timestamp and status update
            'startTime' : datetime.now(),
            'status' : 'Active'
        },
        '$inc' : {'startCount' : 1} # increasing startCount by 1
    } 

    startNewValues = {'$inc' : {'startCount' : 1}} # increasing startCount by 1

    logs.update_one(startQuery, startNewValues) # updating database

    currentStartCount = last2logs[0]['startCount'] # for getting start counts

    if currentStartCount < 1: # so start message doesn't get sent again
        print(color.PURPLE+"Sending start message to resident1...")
        telegramNotificationSend(f"***@{currentUserName}***, your timer has been started. Current date and time: `{datetime.now()}`") 

    return ("startMessage")

#! Start Message for 2. Resident  
@app.route("/startMessageTwo")
@login_required
def startMessageTwo():
    last2logs = []
    for i in logs.find().sort([('$natural', -1)]).limit(2): # query of last 2 logs
        last2logs.append(i)

    currentUserName = last2logs[1]['telegramUsername'] # generating fullname from query to send Telegram notifications
    currentUserId = last2logs[1]['_id'] # getting _id for queries

    startQuery = {'_id' : currentUserId}
    startNewValues = {
        '$set':{ # setting the startTime's value with current timestamp and status update
            'startTime' : datetime.now(),
            'status' : 'Active'
        },
        '$inc' : {'startCount' : 1} # increasing startCount by 1
    } 

    logs.update_one(startQuery, startNewValues) # updating database

    currentStartCount = last2logs[1]['startCount'] # for getting start counts

    if currentStartCount < 1: # so start message doesn't get sent again
        print(color.PURPLE+"Sending start message to resident2...")
        telegramNotificationSend(f"***@{currentUserName}***, your timer has been started. Current date and time: `{datetime.now()}`")

    return ("startMessageTwo")

#! Overtime Message for 1. Resident  
@app.route("/overtimeMessage")
@login_required
def overtimeMessage():
    last2logs = []
    for i in logs.find().sort([('$natural', -1)]).limit(2): # query of last 2 logs
        last2logs.append(i)

    currentUserName = last2logs[0]['telegramUsername'] # generating fullname from query to send Telegram notifications
    currentUserId = last2logs[0]['_id'] # getting _id for queries
    
    overtimeQuery = {'_id' : currentUserId}
    overtimeNewValues = {'$inc' : {'overtimeCount' : 1}} # increasing overtimeCount by 1

    logs.update_one(overtimeQuery, overtimeNewValues) # updating database

    #TODO: After stopping, no more overtime messages.
    currentStopCount = last2logs[0]['stopCount']

    if currentStopCount < 1:
        print(color.PURPLE+"Sending overtime message to resident1...")
        telegramNotificationSend(f"***@{currentUserName}***, your timer has been finished and you are on overtime. Current date and time: `{datetime.now()}`")    

    return ("overtimeMessage")

#! Overtime Message for 2. Resident  
@app.route("/overtimeMessageTwo")
@login_required
def overtimeMessageTwo():
    last2logs = []
    for i in logs.find().sort([('$natural', -1)]).limit(2): # query of last 2 logs
        last2logs.append(i)

    currentUserName = last2logs[1]['telegramUsername'] # generating fullname from query to send Telegram notifications
    currentUserId = last2logs[1]['_id'] # getting _id for queries

    overtimeQuery = {'_id' : currentUserId}
    overtimeNewValues = {'$inc' : {'overtimeCount' : 1}} # increasing overtimeCount by 1

    logs.update_one(overtimeQuery, overtimeNewValues) # updating database

    #TODO: After stopping, no more overtime messages.
    currentStopCount = last2logs[1]['stopCount']

    if currentStopCount < 1:
        print(color.PURPLE+"Sending overtime message to resident2...")
        telegramNotificationSend(f"***@{currentUserName}***, your timer has been finished and you are on overtime. Current date and time: `{datetime.now()}`")

    return ("overtimeMessageTwo")

#! Stop Message for 1. Resident  
@app.route("/stopMessage")
@login_required
def stopMessage():
    last2logs = []
    for i in logs.find().sort([('$natural', -1)]).limit(2): # query of last 2 logs
        last2logs.append(i)

    currentUserName = last2logs[0]['telegramUsername'] # generating fullname from query to send Telegram notifications
    currentUserId = last2logs[0]['_id'] # getting _id for queries
    currentUserOvertimes = last2logs[0]['overtimeCount'] # getting overtimeCount for penalty calculation

    endQuery = {'_id' : currentUserId}
    endNewValues = {
        '$set' : {  # setting the endTime's value with current timestamp and status update
            'endTime' : datetime.now(),
            'status' : 'Terminated'
        },
        '$inc' : {'stopCount' : 1} # increasing stopCount by 1
    }

    logs.update_one(endQuery, endNewValues) # updating database

    currentStopCount = last2logs[0]['stopCount'] # for getting stop counts

    if currentStopCount < 1: # so stop message doesn't get sent again
        print(color.PURPLE+"Sending stop message to resident1...")
        telegramNotificationSend(f"***@{currentUserName}***, your timer has been stopped. Current date and time: `{datetime.now()}`")

        if currentUserOvertimes > 0: # Check the overtimeCount here and send a final message says the total overtimed hours.
            telegramNotificationSend(f"***@{currentUserName}***, you are {currentUserOvertimes} hours late. Total penalty is: `{currentUserOvertimes*5} PLN`.")

    #? Testing below -> Trying to get actual time past in backend and saving it to the db.
    # currentStartTime = last2logs[0]['startTime'].strftime("%S") #? only getting seconds(trimming as str)
    # currentEndTime = last2logs[0]['endTime'].strftime("%S")

    # print(f"Start: {currentStartTime}\nStop: {currentEndTime}")
    # print(f"Time difference: {(float(currentEndTime)-float(currentStartTime))}")

    return ("stopMessage")

#! Stop Message for 2. Resident  
@app.route("/stopMessageTwo")
@login_required
def stopMessageTwo(): 
    last2logs = []
    for i in logs.find().sort([('$natural', -1)]).limit(2): # query of last 2 logs
        last2logs.append(i)

    currentUserName = last2logs[1]['telegramUsername'] # generating fullname from query to send Telegram notifications
    currentUserId = last2logs[1]['_id'] # getting _id for queries
    currentUserOvertimes = last2logs[1]['overtimeCount'] # getting overtimeCount for penalty calculation

    endQuery = {'_id' : currentUserId}
    endNewValues = {
        '$set' : {  # setting the endTime's value with current timestamp and status update
            'endTime' : datetime.now(),
            'status' : 'Terminated'
        },
        '$inc' : {'stopCount' : 1} # increasing stopCount by 1
    }

    logs.update_one(endQuery, endNewValues) # updating database

    currentStopCount = last2logs[1]['stopCount'] # for getting stop counts

    if currentStopCount < 1: # so stop message doesn't get sent again
        print(color.PURPLE+"Sending stop message to resident2...")
        telegramNotificationSend(f"***@{currentUserName}***, your timer has been stopped. Current date and time: `{datetime.now()}`")

        if currentUserOvertimes > 0: # Check the overtimeCount here and send a final message says the total overtimed hours.
            telegramNotificationSend(f"***@{currentUserName}***, you are {currentUserOvertimes} hours late. Total penalty is: `{currentUserOvertimes*5} PLN`.")
    
    return ("stopMessageTwo")


#! Logout
@app.route('/logout')
@login_required
def logout():
    session.clear() # Clearing session and logging out
    flash("Logout successful.","success")
    return redirect(url_for("index"))


#! Flask run
if __name__ == "__main__":
    app.run(debug=True)  #! Make it debug=False on Production Mode
