import pymongo
import bcrypt
import pandas as pd
import collections
import smsConfig
import re
from bson import Binary
from functools import wraps
from datetime import datetime, date
from itsdangerous import SignatureExpired, URLSafeTimedSerializer
from twilio.rest import Client
from flask import Flask, render_template, url_for, request, session, redirect
from flask_mail import Mail,Message

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

mail = Mail(app)

s = URLSafeTimedSerializer('GOMOGOMONO...')

salt = b'$2b$11$Za4hFNuzn3Rvw7gLnUVZCu'

newpassword = None
dbEmail = ""
postSession = ""
sess = {"logged_in":False}

#one-time MongoDB connection
client = pymongo.MongoClient("mongodb://theophilus:chidi18@ds153380.mlab.com:53380/mongo")
db = client['mongo']

#Unrouted functions
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if sess['logged_in'] is True:
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
    status = None
    post = db.Vacancies.find()
    vac = []

    for i in post:
        position = i['post']
        minimum_requirements = i['minimum requirements']
        responsibilities = i['responsibilities']
        deadline = i['deadline']
        apply_url = url_for('test', token = position, _external = False)

        current = datetime.now()

        if current < deadline:
            status = "Active Vacancy"
            vac.append((position, minimum_requirements, responsibilities, apply_url))
        else:
            status = "Expired Vacancy"

    return render_template('index.html', post=vac)


@app.route('/humanResourceHome')
@login_required
def humanResourceHome():
    global postSession
    postSession = ""
    status = None
    post = db.Vacancies.find()
    vac = []

    for i in post:
        position = i['post']
        minimum_requirements = i['minimum requirements']
        responsibilities = i['responsibilities']
        deadline = i['deadline']
        add_url = url_for('temporary', token = position, _external = False)
        edit_url = url_for('edit', token = position, _external = False)

        current = datetime.now()

        if current < deadline:
            status = "Active Vacancy"
        else:
            status = "Expired Vacancy"

        vac.append((position, minimum_requirements, responsibilities, deadline, status, add_url, edit_url))

    return render_template('hr.html', post=vac)

@app.route('/addVacancy', methods=('GET', 'POST'))
def addVacancy():

    if request.method == 'POST':
        post = request.form.get('post')
        department = request.form.get('department')
        requirements = (request.form.get('requirement')).split("\r\n")
        responsibilities = (request.form.get('responsibilities')).split("\r\n")

        dateOfDeadline = request.form.get('deadline')

        deadlineDate = dateOfDeadline.split("-")

        c = []

        for i in deadlineDate:
            c.append(int(i))

        deadline = datetime(c[0], c[1], c[2], 11, 59, 59)
        db.Vacancies.insert({"post":post, "department":department, "deadline":deadline, "minimum requirements":requirements, "responsibilities":responsibilities})

    return render_template('addvacancy.html')

@app.route('/shortlist', methods=('GET', 'POST'))
def shortlist():
    app.jinja_env.globals.update(zip=zip)
    post = postSession
    query = db.applicants.find({"post":post, "$or": [{"status":"new"}, {"status":"reserved"}]})

    applicants = []
    x = []

    for i in query:
        applicants.append(i['name'])

    for i in range(len(applicants)):
        x.append(i)

    if request.method == 'POST':
        for i in x:
            if request.form.get(str(i)) == 'shortlist':
                name = applicants[i]
                db.applicants.update({"name":name}, {"$set":{"status":"shortlist"}})
            if request.form.get(str(i)) == 'denied':
                name = applicants[i]
                db.applicants.update({"name":name}, {"$set":{"status":"denied"}})

        #sending emails for rejection and acceptance


        return redirect(url_for('humanResourceHome'))
    return render_template('shortlist.html', x=x, y=applicants)

@app.route('/resetPassword')
def resetPassword():
    global newpassword

    if newpassword != None:
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

@app.route('/test/<token>')
def test(token):
	'''keeps track of all the posts clicked for application or for editing vacancy'''
	global postSession
	postSession = token
	return redirect(url_for('apply'))

@app.route('/temporary/<token>')
def temporary(token):
	'''keeps track of all the posts clicked for application or for editing vacancy'''
	global postSession
	postSession = token
	return redirect(url_for('shortlist'))

@app.route('/edit/<token>')
def edit(token):
	'''keeps track of all the posts clicked for application or for editing vacancy'''
	global postSession
	postSession = token
	return redirect(url_for('editVacancy'))

@app.route('/newPasswordEntry', methods=('GET', 'POST'))
def newPasswordEntry():

    global newpassword
    if request.method == 'POST':
        newpassword = request.form.get('newpassword2')
        return redirect(url_for('resetPassword'))
    return render_template('newpassword.html')


@app.route('/apply', methods=('GET', 'POST'))
def apply():
    if request.method == 'POST':

        name =  '''{} {}'''.format(request.form.get('firstname'),request.form.get('surname'))
        contacts = '''{} , {} , {} , {} '''.format(request.form.get('phone1'), request.form.get('phone2') , request.form.get('email'), request.form.get('address'))
        sex = request.form.get('sex')

        current = date.today()
        dateOfBirth = request.form.get('DOB')
        cd = current.strftime('%Y, %m, %d')
        currentDate = cd.split(",")
        dob = dateOfBirth.split("-")
        c = []
        d = []

        for i in currentDate:
            c.append(int(i))
        for i in dob:
            d.append(int(i))

        #dynamic entry of age
        age = int((date(c[0], c[1], c[2]) - date(d[0], d[1], d[2])).days / 365)

        #qualifications

        qualifications = ""
        institution = ""
        workexperience = ""
        file = request.files.get('cv')

        cv = Binary(bytes(file.read()))

        if cv != "" or cv is not None:
            comments = "CV & Certificates attached"


        #applyFor = post
        status = "new"

        for i in range(1, int(request.form.get('numberOfQualifications')) + 1):
            qualifications += "{}. ".format(str(i)) + request.form.get('qualification{}'.format(i)) + ". "
            institution += "{}. ".format(str(i)) + request.form.get('awardingInstitute{}'.format(i)) + ". "
        for i in range(1, int(request.form.get('numberOfWorkExperiences')) + 1):
            workexperience += "{}. Worked at {} as {} since {}. ".format(i, request.form.get('organisation{}'.format(i)), request.form.get('position{}'.format(i)), request.form.get('timeframe{}'.format(i)) )

            user = db.applicants.find_one({'National_id':request.form.get('nationalid')})

            if user == None :
	            db.applicants.insert({'name':name, 'contact details':contacts, 'sex':sex, 'age':age,'National_id':request.form.get('nationalid'), 'academic qualifications':qualifications, 'awarding institute':institution, 'work experience':workexperience, 'curriculum vitae':cv, 'comments':comments, 'status':status, 'post':postSession})
            return "application succesful"

    return render_template('applicationform.html')

@app.route('/applicantList')
def applicantList():
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
    df = df.drop(["_id", "curriculum vitae", "status"], axis=1)
    pd.set_option("max_colwidth", 500)

    fullList = df.to_html()
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
                sess['logged_in'] = True
                return redirect(url_for('humanResourceHome'))
        else:
            error_message = 'Invalid Credentials. Please try again.'

    return render_template('login.html', Error_Message=error_message, System_Name="")

@app.route('/editVacancy', methods=('GET', 'POST'))
def editVacancy():

    post = postSession
    query = db.Vacancies.find_one({"post":post})

    posts = []
    posts.extend((query['post'], query['department'], "\r\n".join(query['minimum requirements']), "\r\n".join(query['responsibilities']), (query['deadline']).date(), (query['interview date']).date()))

    if request.method == 'POST':

        dateOfDeadline = request.form.get('deadline')
        dateOfInterview = request.form.get('interviewdate')

        deadlineDate = dateOfDeadline.split("-")
        c = []

        for i in deadlineDate:
            c.append(int(i))

        deadline = datetime(c[0], c[1], c[2], 11, 59, 59)

        requirements = (request.form.get('requirement').split('\r\n'))
        responsibilities = (request.form.get('responsibilities').split('\r\n'))

        db.Vacancies.update({"post":post}, {"$set":{"minimum requirements":requirements, "responsibilities":responsibilities, "deadline":deadline}})
        return redirect(url_for('humanResourceHome'))

    return render_template('editvacancy.html', post=posts)

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
    sess.clear()
    return redirect(url_for('login'))

#404 page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
	app.run(debug=True)
