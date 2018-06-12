from flask import Flask, render_template, url_for, request, session, redirect
from flask_mail import Mail,Message
import pymongo
import bcrypt
from itsdangerous import SignatureExpired, URLSafeTimedSerializer

app = Flask(__name__)
app.config.from_pyfile('config.cfg')


mail = Mail(app)


s = URLSafeTimedSerializer('GOMOGOMONO...')

@app.route('/')
def index():
	return "hey"


@app.route('/sending' , methods=['POST','GET'])
def sending():
	''' this function is to recieve email from a form and send a message to that email to get a new password, can use username which will be used to fetch the email address if it exists in the database '''
	email = request.form['email']  #'zchidzix@gmail.com'
	token = s.dumps(email, salt='mymy')

	link = url_for('forgotPassword', token = token , _external = True)	
	msg = Message('App', sender='achidzix',recipients=[email])
	msg.body = "welcome...! {}".format(link)
	mail.send(msg)
	return "Email has been sent to user emal address {}".format(email)

@app.route('/forgotPassword/<token>')
def forgotPassword(token):
	'''this runs from the link sent to the email address'''
	try:
		email = s.loads(token,salt='mymy', max_age = 3600)
		
	except SignatureExpired:
		return "Link Timed Out"	
	return "hie "

@app.route('/login')
def login():
	'''user logs in using username and password'''
    return ''

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
    	#check db

if __name__ == "__main__":
	app.run(debug=True)	

