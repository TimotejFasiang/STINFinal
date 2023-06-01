from flask import Flask, render_template, request, redirect
from formChecks import *
import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute("DROP TABLE IF EXISTS users")
c.execute("DROP TABLE IF EXISTS transactions")
c.execute("""CREATE TABLE IF NOT EXISTS users (
            firstName text, 
            lastName text,
            email text,
            password text,
            currency text,
            securityAnswer text,
            balance integer
            )""")
c.execute("""CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userEmail TEXT,
            transactionType TEXT,
            amount REAL,
            currency TEXT,
            balance REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")

conn.commit()

app = Flask(__name__)
app.secret_key = "my_secret_key"


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        registration_info = [request.form['firstName'], request.form['lastName'], request.form['email'],
                             request.form['password'], request.form['currency'], request.form['securityAnswer']]
        if checkRegistration(registration_info):
            return "Successfully registered"
        else:
            return "Your account already exits, please login"
    else:
        return render_template('register.html')





@app.route('/merchant-setup/', methods=['GET', 'POST'])
def merchant_setup():
    if request.method == 'POST':
        merchant_setup_info = [request.form['currency'], request.form['merchantAccount']]
        setup_merchant(merchant_setup_info)
        return redirect('/merchant-setup/merchant-payment/')
    else:
        return render_template('merchant-setup.html')

@app.route('/merchant-setup/merchant-payment/', methods=['GET', 'POST'])
def merchant_payment():
    if 'merchant_currency' in session:
        if request.method == 'POST':
            merchant_info = [request.form['amount'], request.form['email'], request.form['password']]
            if checkMerchantInfo(merchant_info) == "True":
                return "Successful payment"
            else:
                return checkMerchantInfo(merchant_info)
        else:
            return render_template('merchant-payment.html')
    else:
        return redirect('/merchant-setup/')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_info = [request.form['email'], request.form['password']]
        if checkLogin(login_info):
            return redirect('/security-question/')
        else:
            return "Incorrect email or password"
    else:
        return render_template('login.html')


@app.route('/security-question/', methods=['GET', 'POST'])
def security_question():
    if 'currency' in session and 'securityAnswer' in session and 'balance' in session:
        if request.method == 'POST':
            security_answer_info = [request.form['securityAnswer']]
            if checkSecurityAnswer(security_answer_info):
                return redirect('/account/')
            else:
                return "Incorrect security answer"
        else:
            return render_template('security-question.html')
    else:
        return redirect('/login/')


@app.route('/account/')
def account():
    if 'currency' in session and 'securityAnswer' in session and 'balance' in session:
        return render_template('account.html')
    else:
        return redirect('/login/')


@app.route('/account/deposit/', methods=['GET', 'POST'])
def deposit():
    if 'currency' in session and 'securityAnswer' in session and 'balance' in session:
        if request.method == 'POST':
            deposit_info = [request.form['amount'], request.form['currency']]
            if checkDeposit(deposit_info):
                return "Successful deposit"
            else:
                return "Deposit error"
        else:
            return render_template('deposit.html')
    else:
        return redirect('/login/')


@app.route('/account/bank-statement/')
def bank_statement():
    if 'currency' in session and 'securityAnswer' in session and 'balance' in session:
        # Retrieve the transaction history from the "transactions" table for the current user
        transactions = getTransactions()
        return render_template('bank-statement.html', transactions=transactions)
    else:
        return redirect('/login/')


app.run()
