from flask import Flask, render_template, url_for, session, flash, request, redirect
import bcrypt
import pymongo
from functools import wraps


#Flask object and configuration
app = Flask(__name__)

#Cross-Site Request Forgery prevention
app.config['SECRET_KEY'] = 'secret key'
#global variables
<<<<<<< HEAD
salt = b'$2b$11$Za4hFNuzn3Rvw7gLnUVZCu'

=======
dbUsername = 'admin'
cost = 11
salt = b'$2b$11$Za4hFNuzn3Rvw7gLnUVZCu'
dbPassword = b'$2b$11$Za4hFNuzn3Rvw7gLnUVZCuv7B3iGvalQ6nMUss0o7/9OcsoBDc/Hi'
>>>>>>> b405a37af2ad86a980d62d65dd4de9076dad6f48

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

#Routed functions
@app.route('/login', methods=('GET', 'POST'))
def login():
    error = ""
    #MongoDB password retrieval
    client = pymongo.MongoClient('mongodb://theophilus:chidi18@ds153380.mlab.com:53380/mongo')
    #accessing mongo database using dictionary style
    db = client['mongo']


    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.hashpw(request.form['password'].encode('utf-8'), salt)
<<<<<<< HEAD
        user = db.Credentials.find({'username': username})
        for i in user:
            dbUsername = i['username']
            dbPassword = bytes(i['password'].encode('utf-8'))
=======
>>>>>>> b405a37af2ad86a980d62d65dd4de9076dad6f48

        if username != dbUsername or  bcrypt.hashpw(request.form['password'].encode('utf-8'), password) != dbPassword:
            error = 'Invalid Credentials. Please try again.'
        else:
            return "Successfully Logged In"
    return render_template('login.html', Error_Message=error, System_Name="")


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/resetpassword')
def resetpassword():
    return render_template('resetpassword.html')

if __name__ == "__main__":
    app.run(debug=True)
