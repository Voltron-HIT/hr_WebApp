from flask import Flask, render_template, url_for, session, flash, request, redirect
import bcrypt
from functools import wraps


#Flask object and configuration
app = Flask(__name__)

#Cross-Site Request Forgery prevention
app.config['SECRET_KEY'] = 'secret key'

#global variables
dbUsername = 'admin'
cost = 11
# salt = b'$2b$11$Za4hFNuzn3Rvw7gLnUVZCu'
# dbPassword = b'$2b$11$Za4hFNuzn3Rvw7gLnUVZCuv7B3iGvalQ6nMUss0o7/9OcsoBDc/Hi'

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
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt(cost))

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

if __name__ == "__main__":
    app.run(debug=True)
