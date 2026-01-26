from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

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

@app.route('/login')
def login():
    return render_template('log_in.html')

@app.route('/createaccount')
def createaccount():
    return render_template('create_account.html')



if __name__ == '__main__':
      app.run(host='127.0.0.1', port=5000, debug=True)