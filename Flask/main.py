from cgitb import reset
from click import password_option
from cryptography.fernet import Fernet, MultiFernet
from flask import Flask, render_template, request
import json
import sqlite3
from datetime import datetime

app = Flask(__name__, template_folder=r'/Users/sivasubramaniyan.k/Git_Codes/DEV/Flask/templates/')

DataBase = "/Users/sivasubramaniyan.k/Git_Codes/DEV/Flask/DB/vault.db"
user_table = 'users'
creds_table = 'creds'
time = str(datetime.now())

@app.route('/')
def index():
    return render_template("home.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    print(username)
    print(password)
    connection = sqlite3.connect(DataBase)
    cur = connection.cursor()
    try:
        db_fetch_name = cur.execute(f"select * from '{user_table}' where username = '{username}' ;").fetchone()[1]
        print(db_fetch_name)
        my_password = cur.execute(f"select PASSWORD from '{user_table}' where username = '{username}';").fetchone()[0]
        db_password = my_password.encode()
        key = cur.execute(f" select KEY from '{user_table}' where username = '{username}';").fetchone()[0]
        f = Fernet(key)
        decMessage = f.decrypt(db_password).decode()
        print("Password: ",decMessage)
        connection.close()
        print("User Exists! Proceeding with password validation")
        result = "User Exists! Proceeding with password validation"
        if password == decMessage:
            print("Login Success")
            result = "Login Success"
        else:
            print("Please check the password you mentioned")
            result = "Please check the password you Entered"

    except TypeError:
        print("No Matchign records found...")
        print("User does not exixts")
        result = "User does not exists"

        

    return render_template("dbcreds.html")

@app.route('/add_entry', methods=['POST', 'GET'])
def add_entry():
    connection = sqlite3.connect(DataBase)
    cur = connection.cursor()
    component_name = request.form.get('name')
    password = request.form.get('password')
    db_count = cur.execute(f"select count(*) from '{creds_table}';").fetchone()[0]
    connection.commit()
    connection.close()
    dbpass = password.encode()
    key = Fernet.generate_key()
    f = Fernet(key)
    id = db_count + 1
    encrypted = f.encrypt(dbpass)
    data_tuple = (id,component_name,encrypted,key,time)
    query = f"insert into '{creds_table}' (id, component, password, key, created) values(?,?,?,?,?);"
    try:
        connection = sqlite3.connect(DataBase)
        cur = connection.cursor()
        cur.execute(query, data_tuple)
        connection.commit()
        connection.close()
    except sqlite3.Error as er:
        result = "Error"
    return render_template("dbcreds.html")

@app.route('/signup_page', methods=['POST','GET'])
def signup_page():
    return render_template("signup.html")

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username = request.form.get("username")
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    mobile = request.form.get("mobile")
    password = request.form.get("password")
    dbpass = password.encode()
    key = Fernet.generate_key()
    f = Fernet(key)
    encrypted = f.encrypt(dbpass)
    
    data = {
        'User_Name': username,
        'First_Name': firstname,
        "Last_Name": lastname,
        "Email": email,
        "Mobile": mobile,
        "Password": encrypted.decode(),
        "key": key.decode(),
        "Created_Time": time
    }

    with open("/Users/sivasubramaniyan.k/Git_Codes/DEV/Flask/Data/%s.json" %username, 'w') as file:
        json.dump(data, file)
    try:
        connection = sqlite3.connect("/Users/sivasubramaniyan.k/Git_Codes/DEV/Flask/DB/vault.db")
        cur = connection.cursor()
        db_count = cur.execute("select count(*) from users;").fetchone()[0]
        sqlite_insert_with_param = f"""INSERT INTO '{user_table}'(id, username, email, firstname, lastname, mobile, password, key, created) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        print("Connected to Database")
        id = db_count + 1
        data_tuple = (id,username,email,firstname,lastname,mobile,encrypted.decode(),key.decode(),time)
        print(data_tuple)
        cur.execute(sqlite_insert_with_param, data_tuple)
        connection.commit()
        connection.close()
        result = "Signup Success Please login to proceed"
    except sqlite3.Error as er:
        result = "Error"

    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
