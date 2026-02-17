from flask import Flask,redirect,session, render_template,request,url_for,flash
from config import db_config 
import mysql.connector
import hashlib
import datetime
import re
from decimal import Decimal,InvalidOperation
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
    
def isUserSuspended(user):
    return user["AccessLevel"]==0
def returnBankNameFromSortCode(sc):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bank WHERE SortCode = %s",(sc,))
    bank = cursor.fetchone()
    cursor.close()
    if bank:
        return bank["BankName"]
    else:
        return ""
def returnBankAcc(an,sc):
    if an is not None and sc is not None:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bank_account WHERE SortCode = '"+sc+"' AND AccountNumber = '"+an+"';")
        bankacc = cursor.fetchone()
        cursor.close()
        if bankacc:
            return bankacc
        else:
            return ""
    else:
        return ""
    
def getCurrencyFromID(id):
    if id is not None:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM currency WHERE CurrencyID = '"+id+"';")
        cs = cursor.fetchone()
        cursor.close()
        if cs:
            return cs
        else:
            return ""
    else:
        return ""
def getCurrencyAccFromID(id):
    if id is not None:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM currency_account WHERE CurrencyAccountID = '"+id+"';")
        cs = cursor.fetchone()
        cursor.close()
        if cs:
            return cs
        else:
            return ""
    else:
        return ""
def getLogFromID(id):
    if id is not None:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM log WHERE LogID = '"+id+"';")
        log = cursor.fetchone()
        cursor.close()
        if log:
            return log
        else:
            return ""
    else:
        return ""
def getAllCurrencies():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM currency;")
    currencies = cursor.fetchall()
    cursor.close()
    return currencies
def getAllCurrencyAccountsFromEmail(email):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM currency_account WHERE Email = '"+email+"';")
    CurrencyAccounts = cursor.fetchall()
    cursor.close()
    return CurrencyAccounts

def getOnlyGBPCurrencyAccountsFromEmail(email):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM currency_account WHERE CurrencyID ='GBP' AND Email = '"+email+"';")
    CurrencyAccounts = cursor.fetchall()
    cursor.close()
    return CurrencyAccounts

# misc
def formatConversion(amt):
    str_amt = format(amt,'f')
    if "." not in str_amt:
        return amt+".00"
    else:
        int_num, dec_part = str_amt.split('.')
        dec_part = dec_part[:2]+dec_part[2:].rstrip('0')
        return int_num+"."+dec_part

def generateCurrencyAccountID():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM currency_account;")
    CurrencyAccounts = cursor.fetchall()
    cursor.close()
    numatend = len(CurrencyAccounts)
    while getCurrencyAccFromID("CR"+str(numatend)):
        numatend = numatend+1
    
    return "CR"+str(numatend)
def generateLogID():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM log;")
    logs = cursor.fetchall()
    cursor.close()
    numatend = len(logs)
    while getLogFromID("Log"+str(numatend)):
        numatend = numatend+1
    
    return "Log"+str(numatend)
# input validations
def emailValidChecker(email):
    regExpression_Email = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return (re.match(regExpression_Email,email) is not None)
def userNameValidChecker(name):
    regExpression_Name = r"^[A-Za-z][A-Za-z'-]{1,44}$"# name is varchar(45)
    return re.match(regExpression_Name,name) is not None
def currencyaccountNameValidChecker(name):
    regExpression_Name = r"^[A-Za-z0-9]{4,45}$"# name is varchar(45)
    return re.match(regExpression_Name,"".join(name.split())) is not None
def sortcodeValidChecker(sc):
    regExpression_Name = r"^[0-9]{6}$"
    return re.match(regExpression_Name,sc) is not None
def accountnumberValidChecker(an):
    regExpression_Name = r"^[0-9]{10}$"
    return re.match(regExpression_Name,an) is not None
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
    user = getUserFromEmail(loginChecker())
    if user:
        if isUserSuspended(user):
            return redirect(url_for('suspended'))
        else:
            return render_template('index.html',user = user)
    else:
        return render_template('index.html',user = user)

@app.route('/suspended',methods=["GET","POST"])
def suspended():
    user = getUserFromEmail(loginChecker())
    if user:
        if isUserSuspended(user):
            
            return render_template('suspended.html',user = user)
        else:
            return redirect(url_for('home'))

    else:
        return redirect(url_for('home'))

    

@app.route('/deposit',methods=["GET","POST"])
def deposit():
    user = getUserFromEmail(loginChecker())
    if user:
        if isUserSuspended(user):
            return redirect(url_for('suspended'))
        else:   
            user_CAs = getOnlyGBPCurrencyAccountsFromEmail(user["Email"])
            selectedCA = None
            amounttodeposit = 5
            if request.method =="POST":
                action = request.form.get("action")
                raw_selectCA = request.form["selectCA"]
                selectedCA = getCurrencyAccFromID(raw_selectCA)
                if action == "ConfirmDeposit":
                    if user["UKBankAcc_SortCode"] and user["UKBankAcc_AccountNumber"]:
                        raw_amount = request.form.get("amount", "").strip()
                        try:
                            amounttodeposit = Decimal(raw_amount)
                        except (InvalidOperation,ValueError):
                            flash("Amount invalid, setting to 1.","error")
                            amounttodeposit = 5
                        if amounttodeposit>=5:
                            ##deposit
                            newamt = selectedCA["Balance"]+amounttodeposit
                            conn = mysql.connector.connect(**db_config)
                            cursor = conn.cursor()
                            statement = "UPDATE `transsmartdatabase`.`currency_account` SET `Balance` = %s WHERE `CurrencyAccountID`= %s;"
                            cursor.execute(
                                statement,(newamt,selectedCA["CurrencyAccountID"])
                            )
                                            
                            ##log it
                            cursor.execute(
                                "INSERT INTO `transsmartdatabase`.`log`(`LogID`,`Reciever_SortCode`,`Reciever_AccountNumber`,`CurrencyAccountID_Sender`,`CurrencyAccountID_Reciever`,`Type`,`Amount`,`TransferDateTime`,`Amount2`)VALUES(%s,%s,%s,%s,null,%s,%s,%s,null);",
                                (generateLogID(),user["UKBankAcc_SortCode"],user["UKBankAcc_AccountNumber"],selectedCA["CurrencyAccountID"],"Deposit",amounttodeposit,datetime.datetime.now())
                            )
                            conn.commit()
                            cursor.close()
                            selectedCA = getCurrencyAccFromID(raw_selectCA)

                            flash("Deposit completed.","confirm")
                            
                    else:
                        flash("Set up a UK Bank Account","error")
                        

            return render_template('deposit.html',user = user,selectedCA = selectedCA,user_CAs =user_CAs,amounttodeposit = amounttodeposit)
    else:
        return redirect(url_for('login'))
        

@app.route('/withdraw',methods=["GET","POST"])
def withdraw():
    user = getUserFromEmail(loginChecker())
    if user:
        if isUserSuspended(user):
            return redirect(url_for('suspended'))
        else:
            user_CAs = getAllCurrencyAccountsFromEmail(user["Email"])
            selectedCA = None
            currency = None
            sortcode = ""
            accnum = ""
            amounttowithdraw = 5
            

            if request.method =="POST":
                action = request.form.get("action")
                raw_selectCA = request.form["selectCA"]
                selectedCA = getCurrencyAccFromID(raw_selectCA)
                if selectedCA:
                    currency = getCurrencyFromID(selectedCA["CurrencyID"])
                    if action == "selectBank" or action == "ConfirmWithdraw" or action == "SelectAmount":
                        raw_sc = request.form["sortcode"]
                        raw_an = request.form["accountnumber"]
                        if sortcodeValidChecker(raw_sc) and accountnumberValidChecker(raw_an):
                            sortcode = raw_sc
                            accnum = raw_an
                        else:
                            flash("Invalid sortcode or account number.","error")

                    if action == "ConfirmWithdraw" or action == "SelectAmount":
                        if sortcode and accnum:
                            raw_amount = request.form.get("amount", "").strip()
                            try:
                                amounttowithdraw = Decimal(raw_amount)
                            except (InvalidOperation,ValueError):
                                flash("Amount invalid, setting to 5.","error")
                                amounttowithdraw = 5
                            min_amnt = Decimal("0.01")
                            
                            if action == "ConfirmWithdraw":
                                #Calcs
                                if amounttowithdraw>=5 and amounttowithdraw<=1000:
                                    newamt = selectedCA["Balance"]-amounttowithdraw
                                    if newamt>=0:
                                        conn = mysql.connector.connect(**db_config)
                                        cursor = conn.cursor()
                                        statement = "UPDATE `transsmartdatabase`.`currency_account` SET `Balance` = %s WHERE `CurrencyAccountID`= %s;"
                                        cursor.execute(
                                            statement,(newamt,selectedCA["CurrencyAccountID"])
                                        )
                                                        
                                        ##log it
                                        cursor.execute(
                                            "INSERT INTO `transsmartdatabase`.`log`(`LogID`,`Reciever_SortCode`,`Reciever_AccountNumber`,`CurrencyAccountID_Sender`,`CurrencyAccountID_Reciever`,`Type`,`Amount`,`TransferDateTime`,`Amount2`)VALUES(%s,%s,%s,%s,null,%s,%s,%s,null);",
                                            (generateLogID(),sortcode,accnum,selectedCA["CurrencyAccountID"],"Withdrawal",amounttowithdraw,datetime.datetime.now())
                                        )
                                        conn.commit()
                                        cursor.close()
                                        selectedCA = getCurrencyAccFromID(raw_selectCA)
                                        
                                        flash("Withdrawal completed.","confirm")
                                    else:
                                        flash("Insufficient funds.","error")

                                else:
                                    flash("Amount must be between 5 and 1000","error")

                        else:
                            flash("Bank Account Invalid","error")

            return render_template('withdraw.html',user = user,selectedCA = selectedCA,user_CAs=user_CAs,currency=currency,accnum=accnum,sortcode=sortcode,amounttowithdraw=amounttowithdraw)
    else:
        return redirect(url_for('login'))

@app.route('/transfer',methods=["GET","POST"])
def transfer():
    user = getUserFromEmail(loginChecker())
    if user:
        if isUserSuspended(user):
            return redirect(url_for('suspended'))
        else:
            print("Setting Values")
            user_CAs = getAllCurrencyAccountsFromEmail(user["Email"])
            currencies = getAllCurrencies()
            selectCASending = None
            selectCARecieving = None
            selectCASendingCurrency = None
            displayresult = None
            selectCARecievingCurrency = None
            result = None
            amounttoconv = 1
            if request.method =="POST":
                action = request.form.get("action")
                raw_selectCASending = request.form["selectCASending"]
                raw_selectCARecieving = request.form["selectCARecieving"]
                raw_amount = request.form.get("amount", "").strip()

                selectCASending = getCurrencyAccFromID(raw_selectCASending)
                selectCARecieving = getCurrencyAccFromID(raw_selectCARecieving)
                    
                
                if action =="QuickSwap":
                    temp_SwapCA = selectCARecieving
                    selectCARecieving = selectCASending
                    selectCASending = temp_SwapCA
                #exchange rate fun stuff yay
                if selectCARecieving and selectCASending:
                        selectCASendingCurrency = getCurrencyFromID(selectCASending["CurrencyID"])
                        min_amnt = Decimal("0.01")
                        selectCARecievingCurrency = getCurrencyFromID(selectCARecieving["CurrencyID"])
                        if selectCARecievingCurrency and selectCASendingCurrency:
                            try:
                                amounttoconv = Decimal(raw_amount)
                            except (InvalidOperation,ValueError):
                                flash("Amount invalid, setting to 1.","error")
                                amounttoconv = 1
                            ##maths would want 
                            fromcurrency_OnePound = selectCASendingCurrency["ValueAgainstPound"]
                            result = fromcurrency_OnePound/selectCARecievingCurrency["ValueAgainstPound"]
                            result= (result*amounttoconv)
                            result = (result.quantize(min_amnt))
                            if result<min_amnt:
                                displayresult = "<0.01"
                            else:
                                displayresult = formatConversion(result)
                        
                        if action == "ConfirmTransfer":
                            #check stuff
                            print(result)
                            if min_amnt<=result:
                                newbalsending = selectCASending["Balance"]-amounttoconv
                                newbalrecieving = selectCARecieving["Balance"]+result
                                if newbalsending>=0:
                                    if selectCASending["CurrencyAccountID"] != selectCARecieving["CurrencyAccountID"]:
                                        conn = mysql.connector.connect(**db_config)
                                        cursor = conn.cursor()
                                        statement = "UPDATE `transsmartdatabase`.`currency_account` SET `Balance` = %s WHERE `CurrencyAccountID`= %s;"
                                        cursor.execute(
                                            statement,(newbalsending,selectCASending["CurrencyAccountID"])
                                        )
                                        cursor.execute(
                                            statement,(newbalrecieving,selectCARecieving["CurrencyAccountID"])
                                        )
                                        #TODO Add logs
                                        cursor.execute(
                                            "INSERT INTO `transsmartdatabase`.`log`(`LogID`,`Reciever_SortCode`,`Reciever_AccountNumber`,`CurrencyAccountID_Sender`,`CurrencyAccountID_Reciever`,`Type`,`Amount`,`TransferDateTime`,`Amount2`)VALUES(%s,null,null,%s,%s,%s,%s,%s,%s);",
                                            (generateLogID(),selectCASending["CurrencyAccountID"],selectCARecieving["CurrencyAccountID"],"Transfer",amounttoconv,datetime.datetime.now(),result)
                                        )
                                        conn.commit()
                                        cursor.close()
                                        #refresh
                                        user_CAs = getAllCurrencyAccountsFromEmail(user["Email"])


                                        selectCASending = getCurrencyAccFromID(raw_selectCASending)
                                        selectCARecieving = getCurrencyAccFromID(raw_selectCARecieving)
                                        flash("Transfer completed.","confirm")
                                    else:
                                        flash("Cannot transfer to the same account.","error")
                                else:
                                    flash("Insufficient funds.","error")
                            else:
                                flash("Amount must convert to >=0.01.","error")
                print(selectCARecieving)
                print(selectCASending)


            return render_template('transfer.html',user = user,user_CAs=user_CAs,currencies=currencies,selectCARecieving = selectCARecieving,selectCASending = selectCASending,selectCASendingCurrency = selectCASendingCurrency,selectCARecievingCurrency=selectCARecievingCurrency,result = displayresult, amounttoconv =amounttoconv)
    else:
        return redirect(url_for('login'))

@app.route('/exchange_rates',methods=["GET","POST"])
def exchange_rates():
    user = getUserFromEmail(loginChecker())
    if isUserSuspended(user):
        return redirect(url_for('suspended'))
    else:
        currencies = getAllCurrencies()
        result = None
        fromcurrency = ""
        tocurrency = ""
        amounttoconv = 1
        amountdisplay = amounttoconv
        if request.method =="POST":
            raw_from= request.form["refcurrency"]
            raw_to = request.form["transfercurrency"]
            raw_amount = request.form.get("amount", "").strip()
            string_fromcurrency = raw_from[:3].upper()
            string_tocurrency = raw_to[:3].upper()
            fromcurrency = getCurrencyFromID(string_fromcurrency)
            tocurrency = getCurrencyFromID(string_tocurrency)
            if  (fromcurrency and tocurrency):
                try:
                    amounttoconv = Decimal(raw_amount)
                except (InvalidOperation,ValueError):
                    flash("Amount invalid, setting to 1.","error")
                    amounttoconv = 1

                ratesmap = {c["CurrencyID"]:c["ValueAgainstPound"] for c in currencies}

                ##maths would want 
                fromcurrency_OnePound = ratesmap[string_fromcurrency]
                result = fromcurrency_OnePound/ratesmap[string_tocurrency]
                result= (result*amounttoconv)
                min_amnt = Decimal("0.0000001")
                amountdisplay = formatConversion((amounttoconv.quantize(min_amnt)))
                if result<min_amnt:
                    result= f<"{min_amnt}"
                else:
                    result = formatConversion((result.quantize(min_amnt)))
                    
                

            else:
                flash("Currencies invalid.","error")

        return render_template('exchange_rates.html',user=user,result=result,fromcurrency=fromcurrency,tocurrency=tocurrency,currencies=currencies,amounttoconv=amounttoconv,amountdisplay = amountdisplay)


@app.route('/profile',methods=["GET","POST"])
def profile():
    user = getUserFromEmail(loginChecker())
    if user:
        if isUserSuspended(user):
            return redirect(url_for('suspended'))
        else:
            userbankacc = returnBankAcc(user["UKBankAcc_AccountNumber"],user["UKBankAcc_SortCode"])
            userbankname = returnBankNameFromSortCode(user["UKBankAcc_SortCode"])
            currency = ""
            ##select logs
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM log INNER JOIN currency_account ON log.CurrencyAccountID_Sender = currency_account.CurrencyAccountID INNER JOIN currency ON currency_account.CurrencyID = currency.CurrencyID WHERE log.Type = \"Deposit\" AND currency_account.Email = %s;",
                (user["Email"],)
            )
            depositlogs = cursor.fetchall()
            
            #withdraw
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM log INNER JOIN currency_account ON log.CurrencyAccountID_Sender = currency_account.CurrencyAccountID INNER JOIN currency ON currency_account.CurrencyID = currency.CurrencyID WHERE log.Type = \"Withdrawal\" AND currency_account.Email = %s;",
                (user["Email"],)
            )
            withdrawallogs = cursor.fetchall()
            
            print(depositlogs)
            cursor.close()
            if userbankacc:
                currency = getCurrencyFromID(userbankacc["CurrencyID"])
            if request.method =="POST":
                accountnumber = request.form["accountnumber"]
                sortcode = request.form["sortcode"]
                password = request.form["password"]
                bankacc = returnBankAcc(accountnumber,sortcode)
                

                if bankacc:
                    if bankacc["CurrencyID"] == "GBP":
                        if password == bankacc["Password"]:
                            conn = mysql.connector.connect(**db_config)
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE `transsmartdatabase`.`user` SET `UKBankAcc_AccountNumber` = %s , `UKBankAcc_SortCode` = %s WHERE `Email`= %s;",
                                (accountnumber,sortcode,user["Email"])
                            )
                            conn.commit()
                            cursor.close()
                            return redirect(url_for('profile'))

                        else:
                            flash("Incorrect password.","error")
                            
                    else:
                        flash("The currency in this account is not GBP.","error")
                        
                else:
                    flash("Bank Account not found.","error")

            return render_template('profile.html',user=user,userbankacc = userbankacc,userbankname=userbankname,currency=currency,depositlogs=depositlogs,withdrawallogs=withdrawallogs)
    else:
        return redirect(url_for('home'))
@app.route('/removebankaccount')
def removebankacc():
    user = getUserFromEmail(loginChecker())
    if user:
        if isUserSuspended(user):
            return redirect(url_for('suspended'))
        else:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE `transsmartdatabase`.`user` SET `UKBankAcc_AccountNumber` = null , `UKBankAcc_SortCode` = null WHERE `Email`= %s;",
                (user["Email"],)
            )
            conn.commit()
            cursor.close()
            return redirect(url_for('profile'))
    else:
        return redirect(url_for('home'))
    
@app.route('/logout')
def logout():
    user = getUserFromEmail(loginChecker())
    if user:
        session.clear()
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

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
def createaccount():
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

@app.route('/currencyaccounts',methods=["GET","POST"])
def currencyaccounts():
    user = getUserFromEmail(loginChecker())
    if user:
        user_CAs = getAllCurrencyAccountsFromEmail(user["Email"])
        currencies = getAllCurrencies()
        logs = None
        selectedCA = None
        currency = None
        if request.method =="POST":
            action = request.form.get("action")
            if action == "createCA":
                accname = request.form["accname"]
                currencyid_raw = request.form["currencyid"]
                string_currencyid = currencyid_raw[:3].upper()
                if getCurrencyFromID(string_currencyid):
                    if currencyaccountNameValidChecker(accname):
                        conn = mysql.connector.connect(**db_config)
                        cursor = conn.cursor()
                        caID = generateCurrencyAccountID()
                        cursor.execute(
                            "INSERT INTO `transsmartdatabase`.`currency_account`(`CurrencyAccountID`,`Email`,`Balance`,`AccountName`,`CurrencyID`) VALUES ('"+caID+"','"+user["Email"]+"',0,'"+accname+"','"+string_currencyid+"');" 
                        )
                        conn.commit()
                        cursor.close()
                        user_CAs = getAllCurrencyAccountsFromEmail(user["Email"])
                        flash("Currency account created.","confirm")

                    else:
                        flash("Account name invalid.","error")
                else:
                    flash("Currency invalid.","error")
            elif action == "viewCA":
                raw_selectedCA = request.form["selectCA"]
                selectedCA = getCurrencyAccFromID(raw_selectedCA)
                if selectedCA:
                    currency = getCurrencyFromID(selectedCA["CurrencyID"])
                    ##select logs
                    conn = mysql.connector.connect(**db_config)
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("SELECT * FROM log WHERE Type = \"Transfer\" AND (CurrencyAccountID_Reciever = %s OR CurrencyAccountID_Sender = %s);",(selectedCA["CurrencyAccountID"],selectedCA["CurrencyAccountID"]))
                    logs = cursor.fetchall()
                    cursor.close()

        return render_template('currencyaccounts.html',user=user,user_CAs = user_CAs,currencies=currencies,selectedCA = selectedCA,currency=currency,logs = logs)
    else:
        return redirect(url_for('home'))




if __name__ == '__main__':
      app.run(host='127.0.0.1', port=5000, debug=True)