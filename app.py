import os
from flask import Flask,render_template, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = os.environ.get("PASSWORD")
app.config['MYSQL_DB'] = 'spectral'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

 
mysql = MySQL(app)
 
@app.route('/')
def home():
  return render_template('home.html')


@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        permissions = request.form['permissions']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO employees(Employees_email, Employees_password, Employee_permissions) VALUES(%s, %s)", (email, password, permissions))
        mysql.connection.commit()
        cursor.close()
        return "DONE!"
    
    else:
        return render_template('form.html')
 
@app.route('/add-client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        age = request.form['age']
        gender = request.form['gender']
        supervisor = request.form['supervisor']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO client(client_firstname, client_lastname, client_age, client_gender, client_supervisor) VALUES(%s, %s, %s, %s, %s)", (firstname, lastname, age, gender, supervisor))
        mysql.connection.commit()
        cursor.close()
        return "DONE!"
    
    else:
        return render_template('add-client.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    print(username['username'], password['password'])
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT Employees_id, Employees_permissions FROM employees WHERE Employees_email = %s AND Employees_password = %s", (username['username'], password['password']))
    account = cursor.fetchone()
    print(account)
    if account:
        return(account)
    else:
        return("Incorrect Username or Password")


        
if __name__ == '__main__':
    app.run(debug=True)