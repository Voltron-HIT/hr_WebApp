from flask import Flask, render_template, url_for, request, session, redirect
from flask_mail import Mail,Message
import pymongo
import bcrypt
from functools import wraps
from itsdangerous import SignatureExpired, URLSafeTimedSerializer

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

mail = Mail(app)

s = URLSafeTimedSerializer('GOMOGOMONO...')

salt = b'$2b$11$Za4hFNuzn3Rvw7gLnUVZCu'

newpassword = ""
dbEmail = ""

#Unrouted functions
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Requires login")
            return redirect(url_for('login'))

    return wrap

@app.route('/')
def index():
	'''opens login page'''
	return render_template('login.html')

@app.route('/resetPassword')
def resetPassword():
    global newpassword
    if newpassword != "":
       client = pymongo.MongoClient('mongodb://theophilus:chidi18@ds153380.mlab.com:53380/mongo')
       db = client['mongo']

       #Hashing new password
       newpassword = (bcrypt.hashpw(newpassword.encode('utf-8'), salt)).decode('utf-8')
       db.Credentials.update_one({"_id":dbEmail}, {"$set":{"password":newpassword}})
       newpassword = ""
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

@app.route('/login', methods=('GET', 'POST'))
def login():
	'''user authentication '''
	error_message = ""
	client = pymongo.MongoClient('mongodb://theophilus:chidi18@ds153380.mlab.com:53380/mongo')
	db = client['mongo']
	if request.method == 'POST':
		username = request.form['username']
		password = bcrypt.hashpw(request.form['password'].encode('utf-8'), salt)

		user = db.Credentials.find({'username': username})
		for i in user:
			dbUsername = i['username']
			dbPassword = bytes(i['password'].encode('utf-8'))

		if username != dbUsername or  bcrypt.hashpw(request.form['password'].encode('utf-8'), password) != dbPassword:
			error = 'Invalid Credentials. Please try again.'
		else:
			return "Successfully Logged In"
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
