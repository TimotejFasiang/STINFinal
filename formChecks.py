from flask import session
from forex_python.converter import CurrencyRates
import sqlite3


def convertCurrency(from_currency, to_currency, amount):
    # Create an instance of the CurrencyRates class
    c = CurrencyRates()
    return c.convert(from_currency.upper(), to_currency.upper(), amount)


def checkRegistration(registration_info):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    first_name = registration_info[0]
    last_name = registration_info[1]
    email = registration_info[2]

    # Check if a user with the same first and last name already exists in the database
    c.execute("SELECT * FROM users WHERE firstName=? AND lastName=? AND email=?", (first_name, last_name, email))
    existing_user = c.fetchone()

    if existing_user:
        return False  # User with the same name already exists
    else:
        # Insert the new user into the database
        c.execute("INSERT INTO users (firstName, lastName, email, password, currency, securityAnswer, balance) "
                  "VALUES (?, ?, ?, ?, ?, ?, 0)", registration_info)
        conn.commit()
        return True  # User registration successful


def checkMerchantInfo(merchant_info):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    payment_amount = float(merchant_info[0])
    merchant_currency = merchant_info[1]
    email = merchant_info[3]
    password = merchant_info[4]
    # Check if the provided email and password match a user in the database
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()
    if user:  # email and password match a specific user
        user_currency = user[4]
        current_balance = user[6]
        payment_amount = convertCurrency(merchant_currency, user_currency, float(payment_amount))
        new_balance = current_balance - payment_amount

        if new_balance >= 0:
            # Update the user's balance in the database
            c.execute("UPDATE users SET balance=? WHERE email=?", (new_balance, email))
            conn.commit()
            return "True"  # Funds successfully removed
        else:
            return "Insufficient funds"  # False  # Insufficient funds
    else:
        return "Login credentials are incorrect"  # False  # Login credentials are incorrect


def checkLogin(login_info):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    email = login_info[0]
    password = login_info[1]

    # Check if the provided login (email) and password match a user in the database
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()
    if user:
        # Get all account info for current session
        session['firstName'] = user[0]
        session['lastName'] = user[1]
        session['email'] = user[2]
        session['password'] = user[3]
        session['currency'] = user[4]
        session['securityAnswer'] = user[5]
        session['balance'] = user[6]
        return True  # Login successful
    else:
        return False  # Login failed


def checkSecurityAnswer(security_answer_info):
    # Check if the provided security answer matches the one associated with the current session
    if session['securityAnswer'] == security_answer_info[0]:
        return True  # Security answer is correct
    else:
        return False  # Security answer is incorrect


def checkDeposit(deposit_info):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # update user's balance
    c.execute("SELECT balance FROM users WHERE email=?", [session['email']])
    session['balance'] = c.fetchone()[0]

    deposit_amount = deposit_info[0]
    deposit_currency = deposit_info[1]
    deposit_amount = convertCurrency(deposit_currency, session['currency'], float(deposit_amount))
    new_balance = session['balance'] + deposit_amount
    if float(deposit_info[0]) > 0:
        # Update the user's balance in the database
        c.execute("UPDATE users SET balance=? WHERE email=?", (new_balance, session['email']))
        conn.commit()
        return True
    else:
        return False
