import os
import bcrypt
from flask import Flask,render_template, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app, supports_credentials=True)
 
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

@app.route('/add-client', methods=['POST'])
def add_a_client():
    firstname = request.json['firstName']
    lastname = request.json['lastName']
    age = request.json['age']
    gender = request.json['gender']
    supervisor = request.json['supervisor']
    addressOne = request.json['addressOne']
    addressTwo = request.json['addressTwo']
    city = request.json['city']
    state = request.json['st']
    postal_code = request.json['postalCode']
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO client(client_firstname, client_lastname, client_age, client_gender, client_supervisor) VALUES(%s, %s, %s, %s, %s)", (firstname, lastname, age, gender, supervisor))
    mysql.connection.commit()
    cursor.close()
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM client WHERE client_firstname = %s AND client_lastname = %s AND client_age = %s AND client_gender = %s AND client_supervisor = %s ORDER BY client_id DESC", (firstname, lastname, age, gender, supervisor))
    data = cursor.fetchone()
    client_id = data['client_id']
    cursor.close()
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO addresses(addresses_one, addresses_two, addresses_city, addresses_state, addresses_postal_code, addresses_client_id) VALUES(%s, %s, %s, %s, %s, %s)", (addressOne, addressTwo, city, state, postal_code, client_id))
    mysql.connection.commit()
    cursor.close()
    return ("Client Added")

@app.route("/get-client-address/<id>", methods=['GET'])
def get_client_address(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM addresses WHERE addresses_client_id = %s", [id])
    data = cursor.fetchone()
    return(jsonify(data))

@app.route("/add-client-trial/<id>", methods=['POST'])
def add_client_trial(id):
    trial_name = request.json['name']
    trial_category = request.json['category']
    trial_description = request.json['description']
    client_id = id
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO trial(trial_name, trial_category, trial_description, trial_client_id) VALUES(%s, %s, %s, %s)", (trial_name, trial_category, trial_description, client_id))
    mysql.connection.commit()
    cursor.close()
    return "Added"


@app.route("/add-client-frequency/<id>", methods=['POST'])
def add_client_frequency(id):
    frequency_name = request.json['name']
    frequency_description = request.json['description']
    client_id = id
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO frequency(frequency_name, frequency_description, frequency_client_id) VALUES(%s, %s, %s)", (frequency_name, frequency_description, client_id))
    mysql.connection.commit()
    cursor.close()
    return "Added"


@app.route("/add-client-duration/<id>", methods=['POST'])
def add_client_duration(id):
    duration_name = request.json['name']
    duration_description = request.json['description']
    client_id = id
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO duration(duration_name, duration_description, duration_client_id) VALUES(%s, %s, %s)", (duration_name, duration_description, client_id))
    mysql.connection.commit()
    cursor.close()
    return "Added"

@app.route("/get-frequency/<id>", methods=['GET'])
def get_frequency(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM frequency WHERE frequency_client_id = %s", [id])
    data = cursor.fetchall()
    return (jsonify(data))

@app.route("/get-frequency-instance", methods=['GET'])
def get_frequency_instance():
    if request.args['date']:
        date = request.args['date']
        id = request.args['id']
    else:
        return "GET request is missing arguements"
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM frequency_instance WHERE frequency_instance_date = %s AND frequency_instance_frequency_id = %s;", (date, id))
    data = cursor.fetchone()
    cursor.close()
    if data:
        return (data)
    else:
        return "No data found"

@app.route("/new-frequency-instance", methods=['POST'])
def new_frequency_instance():
    id = request.json['id']
    date = request.json['date']
    data = request.json['data']
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO frequency_instance(frequency_instance_data, frequency_instance_date, frequency_instance_frequency_id) VALUES(%s, %s, %s);", (data, date, id))
    mysql.connection.commit()
    cursor.close()
    return "Added"

@app.route("/update-frequency-instance/<id>", methods=['PATCH'])
def update_frequency_instance(id):
    id = id
    data = request.json['data']
    date = request.json['date']
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE frequency_instance SET frequency_instance_data = %s WHERE frequency_instance_frequency_id = %s AND frequency_instance_date = %s;", (data, id, date))
    mysql.connection.commit()
    cursor.close()
    return "Updated"
        
if __name__ == '__main__':
    app.run(debug=True)