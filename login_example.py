from flask import Flask, render_template, url_for, request, session, redirect
import pymongo
import bcrypt

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'hrlogin'
app.config['MONGO_URI'] = 'mongodb://taps:pass1234@ds255970.mlab.com:55970/hrlogin'

mongo = pymongo(app)

@app.route('/')
def index():
    if 'username' in session:
        return 'You are loggen in as ' + session['username']
    
    return render_template('index.html')

@app.route('/login')
def login():
    return ''

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':

        
if __name__ == '__main__':
    app.secret_key = 'passkey'
    app.run(debug=True)

