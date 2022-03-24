from cgitb import reset
from cryptography.fernet import Fernet, MultiFernet
from flask import Flask, render_template, request
import json
import sqlite3
from datetime import datetime

app = Flask(__name__, template_folder=r'/Users/sivasubramaniyan.k/Git_Codes/Flask/templates/')





@app.route('/')
def index():
    return render_template("home.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    print(username)
    print(password)
    connection = sqlite3.connect("/Users/sivasubramaniyan.k/Git_Codes/Flask/DB/vault.db")
    cur = connection.cursor()
    try:
        db_fetch_name = cur.execute(f"select * from users where username = '{username}' ;").fetchone()[1]
        print(db_fetch_name)
        my_password = cur.execute(f"select PASSWORD from users where username = '{username}';").fetchone()[0]
        db_password = my_password.encode()
        key = cur.execute(f" select KEY from users where username = '{username}';").fetchone()[0]
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
    
        

    return result

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
    time = str(datetime.now())
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

    with open("/Users/sivasubramaniyan.k/Git_Codes/Flask/Data/%s.json" %username, 'w') as file:
        json.dump(data, file)
    
    connection = sqlite3.connect("/Users/sivasubramaniyan.k/Git_Codes/Flask/DB/vault.db")
    cur = connection.cursor()
    db_count = cur.execute("select count(*) from users;").fetchone()[0]
    print(type(db_count))
    sqlite_insert_with_param = """INSERT INTO users(id, username, email, firstname, lastname, mobile, password, key, created) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"""
    print("Connected to Database")
    id = db_count + 1
    data_tuple = (id,username,email,firstname,lastname,mobile,encrypted.decode(),key.decode(),time)
    print(data_tuple)
    cur.execute(sqlite_insert_with_param, data_tuple)
    connection.commit()
    connection.close()

    return data


if __name__ == "__main__":
    app.run(debug=True)
