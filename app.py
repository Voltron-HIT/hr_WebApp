from flask import Flask, render_template, url_for, request, session, redirect
from flask_mail import Mail,Message
import pymongo
import bcrypt
import pandas as pd
import collections
from bson import Binary
import json
import re
from bson import Binary
from functools import wraps
from datetime import datetime, date
from itsdangerous import SignatureExpired, URLSafeTimedSerializer

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

mail = Mail(app)

s = URLSafeTimedSerializer('GOMOGOMONO...')

salt = b'$2b$11$Za4hFNuzn3Rvw7gLnUVZCu'

newpassword = None
dbEmail = ""

#Unrouted functions
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))

    return wrap

@app.route('/')
@app.route('/home')
def home():
    status = None

    client = pymongo.MongoClient("mongodb://theophilus:chidi18@ds153380.mlab.com:53380/mongo")
    db = client['mongo']

    post = db.Vacancies.find()

    vac = []

    for i in post:
        position = i['post']
        minimum_requirements = i['minimum requirements']
        responsibilities = i['responsibilities']
        deadline = i['deadline']

        current = datetime.now()

        if current < deadline:
            status = "Active Vacancy"
        else:
            status = "Expired Vacancy"

        vac.append((position, minimum_requirements, responsibilities, deadline, status))

    return render_template('index.html', post=vac)


@app.route('/humanResourceHome')
def humanResourceHome():
	return render_template('hr.html')

# @app.route('/applicationForm')
# def applicationForm():
# 	return render_template('applicationform.html')

@app.route('/addVacancy')
def addVacancy():
	return render_template('addvacancy.html')

@app.route('/adjudication')
def adjudication():
	return render_template('adjudication.html')

@app.route('/shortlist')
def shortlist():

    client = pymongo.MongoClient("mongodb://theophilus:chidi18@ds153380.mlab.com:53380/mongo")
    db = client['mongo']


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


# @app.route('/capture', methods=['POST', 'GET'])
# def capture():
#
#     client = pymongo.MongoClient('mongodb://theophilus:chidi18@ds153380.mlab.com:53380/mongo')
#     db = client['mongo']
#     if request.method == 'POST':
#         data = request.get_json()
#
#         firstname = data['firstname']
#         surname = data['surname']
#         nationalid = data['nationalid']
#         dob = data['dob']
#         sex = data['sex']
#         email = data['email']
#         phone1 = data['phone1']
#         phone2 = data['phone2']
#         address = data['address']
#         # db.Temporary.insert(request.get_json())
#
#         applicants = db.Temporary.find_one({"firstname": firstname, "surname": surname})
#
#
#         current = date.today()
#         dateOfBirth = applicants['dob']
#         cd = current.strftime('%Y, %m, %d')
#         currentDate = cd.split(",")
#         dob = dateOfBirth.split("-")
#         c = []
#         d = []
#
#         for i in currentDate:
#             c.append(int(i))
#         for i in dob:
#             d.append(int(i))
#
#         #dynamic entry of age
#         age = int((date(c[0], c[1], c[2]) - date(d[0], d[1], d[2])).days / 365)
#         print(age)
#
#         #academic qualifications
#         certificates = []
#         qualifications = applicants['qualifications']
#         print(type(qualifications))
#         academics = ""
#         comments = ""
#
#         for i in range(1, len(qualifications) + 1):
#             s = "qualification" + str(i)
#             academics += "{}.".format(str(i)) + " " + qualifications[s]['qualification'] + " "
#         print(academics)
#
#         for i in range(1, len(qualifications) + 1):
#             s = "qualification" + str(i)
#             c = "certificate"
#
#
#             file = request.files.get(c)
#             bfile = file.read()
#             bitFile = bytes(bfile)
#             certificates.append(Binary(bitFile))
#
#         if certificates != []:
#             comments = "Academic Certificates Attached"
#
#
#
#         db.applicants.insert({'name' :  firstname + ' ' + surname, 'contact details': applicants['email'] + applicants['phone1'] + applicants['phone2'] + applicants['address'], 'sex': applicants['sex'], 'age': age,
#         'academic qualifications': academics, 'certificate': certificates})#,'awarding institute': 'xxx','certificate': certificates,
#         # 'work experience': 'xxx' , 'comments': comments, 'salary': ' '})
#
#
#     return render_template('applicationform.html')

@app.route('/capture', methods=('GET', 'POST'))
def capture():

    client = pymongo.MongoClient('mongodb://theophilus:chidi18@ds153380.mlab.com:53380/mongo')
    db = client['mongo']
    if request.method == 'POST':
        print("Qualification " + request.form.get('numberOfQualifications'))
        print("Work Exprerience " + request.form.get('numberOfWorkExperiences'))
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

        #qualifications = request.form.get('qualification1')
        #workexperience = request.form.get('workexperience')
        file = request.files.get('cv')

        cv = Binary(bytes(file.read()))

        if cv != "" or cv is not None:
            comments = "CV & Certificates attached"


        #applyFor = post
        status = "new"
        #db.applicants.insert({'name':name, 'contact details':contact, 'sex':sex, 'age':age, 'academic qualifications':qualifications, 'work experience':workexperience, 'curriculum vitae':cv, 'comments':comments, 'status':status, 'post':applyFor })
        db.applicants.insert({'name':name, 'contact details':contacts, 'sex':sex, 'age':age, 'curriculum vitae':cv, 'comments':comments, 'status':status})
        return redirect(url_for('home'))
    return render_template('applicationform.html')



@app.route('/applicantList')
def applicantList():

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
