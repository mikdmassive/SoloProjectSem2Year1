from flask import Flask,redirect,session, render_template,request,url_for,flash
from config import db_config 
import mysql.connector
import hashlib
import re
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
# input validations
def emailValidChecker(email):
    regExpression_Email = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return (re.match(regExpression_Email,email) is not None)
def userNameValidChecker(name):
    regExpression_Name = r"^[A-Za-z][A-Za-z'-]{1,44}$"# name is varchar(45)
    return re.match(regExpression_Name,name) is not None
def passwordValidationCheck(password):
    specialChars = "!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
    valid = False
    if any(sc in specialChars for sc in password): #check for special chars
        if password == password.strip():##check ws
            if len(password)>=8 and len(password)<=20:#checklen
                ##valid
                valid = True
    return valid

#links
@app.route('/')
def home():
    return render_template('index.html',user = getUserFromEmail(loginChecker()))

@app.route('/deposit')
def deposit():
    return render_template('deposit.html',user = getUserFromEmail(loginChecker()))

@app.route('/widthdraw')
def widthdraw():
    return render_template('widthdraw.html',user = getUserFromEmail(loginChecker()))

@app.route('/transfer')
def transfer():
    return render_template('transfer.html',user = getUserFromEmail(loginChecker()))

@app.route('/exchange_rates')
def exchange_rates():
    return render_template('exchange_rates.html',user = getUserFromEmail(loginChecker()))

@app.route('/login',methods=["GET","POST"])
def login():
    if loginChecker()=="":
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
    else:
        return redirect(url_for('home'))
@app.route('/createaccount',methods=["GET","POST"])
def createaccount():#
    if loginChecker()=="":
        if request.method =="POST":
            email = request.form["email"]
            fname = request.form["fname"]
            lname = request.form["lname"]
            password = request.form["password"]
            ##validation checks
            if emailValidChecker(email):
                ##valid format
                if getUserFromEmail(email)=="":
                    ##not in use
                    if userNameValidChecker(fname) and userNameValidChecker(lname):
                        ##names valid
                        if passwordValidationCheck(password):
                            ##valid
                            conn = mysql.connector.connect(**db_config)
                            cursor = conn.cursor()
                            cursor.execute(
                                "INSERT IGNORE INTO `transsmartdatabase`.`user`(`Email`,`First_Name`,`Last_Name`,`UKBankAcc_AccountNumber`,`UKBankAcc_SortCode`,`Password`,`AccessLevel`) VALUES ('"+email+"','"+fname+"','"+lname+"',null,null,'"+password+"',1);"
                            )
                            conn.commit()
                            cursor.close()
                            session["user_email"] = email
                            return redirect(url_for('home'))
                        else:
                            flash("Password invalid.","error")

                    else:
                        flash("Name invalid. (2-45 characters)","error")
                        flash("Ensure to use only A-Z, ', and -.","error")
                else:
                    flash("Email in use.","error")
            else:
                flash("Email invalid.","error")
    
        return render_template('create_account.html')
    else:
        return redirect(url_for('home'))



    



if __name__ == '__main__':
      app.run(host='127.0.0.1', port=5000, debug=True)