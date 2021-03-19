import os
import bcrypt
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
        hashed = bcrypt.hashpw(password.encode(encoding = "UTF-8"), bcrypt.gensalt())
        permissions = request.form['permissions']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO employees(Employees_email, Employees_password, Employees_permissions) VALUES(%s, %s, %s)", (email, hashed, permissions))
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
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT Employees_id, Employees_permissions, Employees_password FROM employees WHERE Employees_email = %s",[ username['username'] ])
    account = cursor.fetchone()
    data = {
        "id": account["Employees_id"],
        "permissions": account["Employees_permissions"]
    }
    c_password = password["password"]
    password_check = c_password.encode(encoding = "UTF-8")
    stored_password = account["Employees_password"]
    stored_password_check = stored_password.encode(encoding = "UTF-8")
    if bcrypt.checkpw(password_check, stored_password_check):
        return(data)
    else:
        return("Incorrect Username or Password")

@app.route('/clients', methods=['GET'])
def clients():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM client")
    clients = cursor.fetchall()
    return(jsonify(clients))

@app.route('/clients/<id>', methods=['GET'])
def individual_client(id):
    client_id = id
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM client WHERE client_id = %s", [client_id])
    client = cursor.fetchone()
    return(jsonify(client))
        
if __name__ == '__main__':
    app.run(debug=True)