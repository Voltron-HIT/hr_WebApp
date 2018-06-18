from flask import Flask, render_template, url_for, request, session, redirect
from flask_mail import Mail,Message
import pymongo
import bcrypt
import pandas as pd
import collections
import re
from bson import Binary
import smsConfig
from functools import wraps
from datetime import datetime
from itsdangerous import SignatureExpired, URLSafeTimedSerializer
from twilio.rest import Client

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

mail = Mail(app)

s = URLSafeTimedSerializer('GOMOGOMONO...')

salt = b'$2b$11$Za4hFNuzn3Rvw7gLnUVZCu'

newpassword = None
dbEmail = ""
postSession = ""

#Unrouted functions
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))

    return wrap

def smss(sendTo):
	'''uses one phone number for a free trail, function used in other functions as a extra feature'''
	account_sid = smsConfig.accountSID
	auth_token = smsConfig.authToken
	client = Client(account_sid, auth_token)
	message = client.messages.create(body='Hello there!',from_=smsConfig.twilioNumber,to='+263784428853')
	return message.sid

@app.route('/')
@app.route('/home')
def home():
    global postSession
    postSession = ""

    position = ""
    deadline = None
    status = None
    minimum_requirements = []
    responsibilities = []

    client = pymongo.MongoClient("mongodb://theophilus:chidi18@ds153380.mlab.com:53380/mongo")
    db = client['mongo']

    post = db.Vacancies.find()

    for i in post:
        position = i['post']
        minimum_requirements = i['minimum requirements']
        responsibilities = i['responsibilities']
        deadline = i['deadline']
        apply_url = url_for('test',token = i['post']  , _external = False)
        current = datetime.now()

        if current < deadline:
            status = "Active Vacancy"
        else:
            status = "Expired Vacancy"

    return render_template('index.html', minimum_requirements=minimum_requirements, responsibilities=responsibilities, position=position, status=status, deadline=deadline,apply_url=apply_url)


@app.route('/test/<token>')
def test(token):
	'''keeps track of all the posts clicked for application or for editing vacancy'''
	global postSession
	postSession = token
	return redirect(url_for('applicationForm'))


@app.route('/humanResourceHome')
def humanResourceHome():
    global postSession
    postSession = ""

    position = ""
    deadline = None
    status = None
    minimum_requirements = []
    responsibilities = []

    client = pymongo.MongoClient("mongodb://theophilus:chidi18@ds153380.mlab.com:53380/mongo")
    db = client['mongo']

    post = db.Vacancies.find()

    for i in post:
        position = i['post']
        minimum_requirements = i['minimum requirements']
        responsibilities = i['responsibilities']
        deadline = i['deadline']
        apply_url = url_for('test',token = i['post']  , _external = False)
        current = datetime.now()

        if current < deadline:
            status = "Active Vacancy"
        else:
            status = "Deadline Pasted"

    return render_template('hr.html', minimum_requirements=minimum_requirements, responsibilities=responsibilities, position=position, status=status, deadline=deadline,apply_url=apply_url)


@app.route('/applicationForm')
def applicationForm():
	return render_template('applicationform.html')

@app.route('/addVacancy')
def addVacancy():
	return render_template('addvacancy.html')

@app.route('/adjudication')
def adjudication():
	return render_template('adjudication.html')

@app.route('/shortlist')
def shortlist():
	return render_template('shortlist.html')

@app.route('/resetPassword')
def resetPassword():
    global newpassword

    if newpassword != None:
       client = pymongo.MongoClient('mongodb://theophilus:chidi18@ds153380.mlab.com:53380/mongo')
       db = client['mongo']

       #Hashing new password
       newpassword = (bcrypt.hashpw(newpassword.encode('utf-8'), salt)).decode('utf-8')
       db.Credentials.update_one({"_id":dbEmail}, {"$set":{"password":newpassword}})
       newpassword = None
       return redirect(url_for('login'))
    return render_template('resetpassword.html')

@app.route('/passwordRecovery', methods = ['GET','POST'])
def passwordRecovery():
	'''verifies the email adress and sent the password '''
	email = ""
	if request.method == 'POST':
		email = request.form['email']
	token = s.dumps(email, salt = 'emailRecovery')
	return redirect(url_for('sending',token = token , _external = False))

@app.route('/sending/<token>')
def sending(token):
    '''this function sends a message to that email to get a new password, can use username which will be used to fetch the email address if it exists in the database '''

    global dbEmail


    email = s.loads(token, salt = 'emailRecovery')
    token = s.dumps(email, salt='emailToLink')
    dbEmail = email

    link = url_for('forgotPassword', token = token , _external = True)
    msg = Message('Email Verification', sender='achidzix',recipients=[email])
    msg.body = "User associated with the #@$ account has iniated a request to recover user password.\nTo complete password recover process, click the following link to enter new password \n{} \n\nFor your account protection, this link will expire after 24 hours.\n\nBest regards\nHIT\n\nhttps://www.hit.ac.zw/".format(link)
    mail.send(msg)
    return "Email has been sent to user emal address {}".format(email)

@app.route('/forgotPassword/<token>')
def forgotPassword(token):
	'''this runs from the link sent to the email address'''
	try:
		email = s.loads(token,salt='emailToLink', max_age = 3600)

	except SignatureExpired:
		return "Link Timed Out"
	return render_template('newpassword.html')

@app.route('/newPasswordEntry', methods=('GET', 'POST'))
def newPasswordEntry():

    global newpassword
    if request.method == 'POST':
        newpassword = request.form.get('newpassword2')
        return redirect(url_for('resetPassword'))
    return render_template('newpassword.html')


@app.route('/capture', methods=['POST', 'GET'])
def capture():
    '''collects data from the application form and saves it to the database'''
    global postSession
    class Applicants(db.Model):
        __tablename__ = 'employees'
		
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(60), index=True)
        contactdetails = db.Column(db.String(60), index=True)
        national_id = db.Column(db.String(60), index=True, unique=True)
        sex = db.Column(db.String(60), index=True)
        age = db.Column(db.String(60), index=True)
        academic_qualifications = db.Column(db.String(60), index=True)
        awarding_institute = db.Column(db.String(60), index=True)
        certificate = db.Column(db.String(60), index=True)
        work_experience = db.Column(db.String(60), index=True)

    if request.method == 'POST':
        data = request.get_json()
        print(data)
        return 'Application Successful'
    
    return render_template('applicationform.html')



@app.route('/applicantList')
def applicantList():
    '''shows the list of applicants saved to the database'''
    client = pymongo.MongoClient("mongodb://theophilus:chidi18@ds153380.mlab.com:53380/mongo")
    db = client['mongo']
    user = db.applicants.find({})
    data = []
    keys = []
    values = []
    
    

    for i in user:
        keys = list(i.keys())
        values = list(i.values())
        dictionary = dict(zip(values, keys))

        data.append(collections.OrderedDict(map(reversed, dictionary.items())))
    
    df = pd.DataFrame(data)
    df = df.drop(["_id"], axis=1)
    #pd.set_option('max_colwidth', 1000)



    fullList = df.to_html()
    pattern = r'"dataframe"'
    fullList = re.sub(pattern, "dataframe ", fullList)


    path = 'templates/applicantList/applicantlist.html'
    file = 'applicantList/applicantlist.html'

    with open(path, 'w') as myfile:
        myfile.write('''{% extends "list.html" %}
                        {% block title %} Full Applicant List {% endblock %}
                        {% block heading %} Applicant List {% endblock %}
                        {% block content %}
                        ''')
        myfile.write(fullList)
        myfile.write('{% endblock %}')

    return render_template(file)

@app.route('/login', methods=('GET', 'POST'))
def login():
    '''verifies entered credentials with that in the database'''
    error_message = ""
    #MongoDB password retrieval
    client = pymongo.MongoClient('mongodb://theophilus:chidi18@ds153380.mlab.com:53380/mongo')
    #accessing mongo database using dictionary style
    db = client['mongo']

    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.hashpw(request.form['password'].encode('utf-8'), salt)
        user = db.Credentials.find_one({'username': username})

        if user != None :
            dbUsername = user['username']
            dbPassword = bytes(user['password'].encode('utf-8'))

            if username != dbUsername or bcrypt.hashpw(request.form['password'].encode('utf-8'), password) != dbPassword:
                error_message = 'Invalid Credentials. Please try again.'
            else:
                return redirect(url_for('humanResourceHome'))
        else:
            error_message = 'Invalid Credentials. Please try again.'

    return render_template('login.html', Error_Message=error_message, System_Name="")

	
@app.route('/adjudicate')
@login_required
def adjudicate():
	class Adjudication(db.Model):
		__tablename__ = 'adjudication'
		
		id = db.Column(db.Integer, primary_key=True)
		name = db.Column(db.String(60), index=True)
		contactdetails = db.Column(db.String(60), index=True)
		marks = db.column(db.String(60), index=True)

		
@app.route('/adduser')
@login_required
def adduser():
	class Credentials(db.Model):
		__tablename__ = 'credentials'
		
		id = db.Column(db.Integer, primary_key=True)
		username = db.Column(db.String(60), index=True ,unique=True)
		password = db.Column(db.String(60), index=True)
		email = db.Column(db.String(60), index=True, unique=True)
			

@app.route('/addvancy')
@login_required
def addvacancy():
	class Vacancy(db.Model):
		__tablename__='vacancy'
		
		id = db.Column(db.Integer, primary_key=True)
		post = db.Column(db.String(60), index=True ,unique=True)
		department = db.Column(db.String(60), index=True)
		deadline = db.Column(db.String(60), index=True)
		mini_requirements = db.Column(db.String(60), index=True)
		responsibilites = db.Column(db.String(60), index=True)
	   
	   # adjudicator details 
		name= db.Column(db.String(60), index=True)
		adju_post=db.Column(db.String(60), index=True)
		intervw_date=db.Column(db.datetime)


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

#404 page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
	app.run(debug=True)
