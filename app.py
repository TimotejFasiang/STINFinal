from flask import Flask, render_template, request, redirect
from formChecks import *
import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()
# TODO: if table "users" already exists, but has different info, program will not function
c.execute("""CREATE TABLE IF NOT EXISTS users (
            firstName text,
            lastName text,
            email text,
            password text,
            currency text,
            securityAnswer text,
            balance integer
            )""")
conn.commit()

app = Flask(__name__)


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


@app.route('/merchant-payment/', methods=['GET', 'POST'])
def merchant_payment():
    if request.method == 'POST':
        merchant_info = [request.form['amount'], request.form['currency'], request.form['merchantAccount'],
                         request.form['email'], request.form['password']]
        if checkMerchantInfo(merchant_info) == True:
            return "Successful payment"
        else:
            return checkMerchantInfo(merchant_info)
    else:
        return render_template('merchant-payment.html')


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
    if request.method == 'POST':
        security_answer_info = [request.form['securityAnswer']]
        if checkSecurityAnswer(security_answer_info):
            return redirect('/account/')
        else:
            return "Incorrect security answer"
    else:
        return render_template('security-question.html')


@app.route('/account/')
def account():
    return render_template('account.html')


@app.route('/account/deposit/', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        deposit_info = [request.form['amount'], request.form['currency']]
        if checkDeposit(deposit_info):
            return "Successful deposit"
        else:
            return "Deposit error"
    else:
        return render_template('deposit.html')


@app.route('/account/bank-statement/')
def bank_statement():
    return render_template('bank-statement.html')


app.run()
