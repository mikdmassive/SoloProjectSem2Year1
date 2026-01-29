from flask import Flask,redirect,session, render_template,request,url_for,flash
from config import db_config 
import mysql.connector
import hashlib
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
def getUserFromEmail(email):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user WHERE Email = %s",(email,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return user
    else:
        return ""
def loginChecker():
    if "user_email" not in session:
        return ""
    else:
        return session["user_email"]
@app.route('/')
def home():
    return render_template('index.html',user = getUserFromEmail(loginChecker()))

@app.route('/deposit')
def deposit():
    return render_template('deposit.html')

@app.route('/widthdraw')
def widthdraw():
    return render_template('widthdraw.html')

@app.route('/transfer')
def transfer():
    return render_template('transfer.html')

@app.route('/exchange_rates')
def exchange_rates():
    return render_template('exchange_rates.html')

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method =="POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Email,Password FROM user WHERE Email = %s",(email,)
        )
        user = cursor.fetchone()
        cursor.close()
        if user:
            if password == user[1]:
                session["user_email"] = user[0]
                return redirect(url_for('home'))
            else:
                flash("Incorrect Password","error")
                
        else:
            flash("Email not found.","error")

    return render_template('log_in.html')

@app.route('/createaccount')
def createaccount():
    return render_template('create_account.html')



if __name__ == '__main__':
      app.run(host='127.0.0.1', port=5000, debug=True)