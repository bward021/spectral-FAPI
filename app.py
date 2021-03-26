import os
import bcrypt
from flask import Flask,render_template, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app, supports_credentials=True)
 
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST') or 'localhost'
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

@app.route("/get-all-client-trials/<id>", methods=['GET'])
def get_all_client_trials(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM trial WHERE trial_client_id = %s", [id])
    data = cursor.fetchall()
    cursor.close()
    return (jsonify(data))

@app.route("/check-trial-instance", methods=['GET'])
def check_trial_instance():
    if request.args['date']:
        date = request.args['date']
        id = request.args['id']
    else:
        return "GET request is missing arguements"
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM trial_instance WHERE trial_instance_date = %s AND trial_instance_trial_id = %s;", (date, id))
    data = cursor.fetchone()
    cursor.close()
    if data:
        return (data)
    else:
        return "No data found"

@app.route("/new-trial-instance", methods=['POST'])
def new_trial_instance():
    id = request.json['id']
    date = request.json['date']
    incorrect = request.json['incorrect']
    prompted = request.json['prompted']
    correct = request.json['correct']
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO trial_instance(trial_instance_correct, trial_instance_prompted, trial_instance_incorrect, trial_instance_date, trial_instance_trial_id) VALUES(%s, %s, %s, %s, %s);", (correct, prompted, incorrect, date, id))
    mysql.connection.commit()
    cursor.close()
    return "Added"

@app.route("/update-trial-instance-incorrect", methods=['PATCH'])
def update_trial_instance_incorrect():
    id = request.json['id']
    data = request.json['data']
    date = request.json['date']
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE trial_instance SET trial_instance_incorrect = %s WHERE trial_instance_trial_id = %s AND trial_instance_date = %s;", (data, id, date))
    mysql.connection.commit()
    cursor.close()
    return "Updated"

@app.route("/update-trial-instance-prompted", methods=['PATCH'])
def update_trial_instance_prompted():
    id = request.json['id']
    data = request.json['data']
    date = request.json['date']
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE trial_instance SET trial_instance_prompted = %s WHERE trial_instance_trial_id = %s AND trial_instance_date = %s;", (data, id, date))
    mysql.connection.commit()
    cursor.close()
    return "Updated"

@app.route("/update-trial-instance-correct", methods=['PATCH'])
def update_trial_instance_correct():
    id = request.json['id']
    data = request.json['data']
    date = request.json['date']
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE trial_instance SET trial_instance_correct = %s WHERE trial_instance_trial_id = %s AND trial_instance_date = %s;", (data, id, date))
    mysql.connection.commit()
    cursor.close()
    return "Updated"

@app.route("/get-all-client-duration/<id>", methods=['GET'])
def get_all_client_duration(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM duration WHERE duration_client_id = %s", [id])
    data = cursor.fetchall()
    cursor.close()
    return (jsonify(data))

@app.route("/new-duration-instance", methods=['POST'])
def new_duration_instance():
    id = request.json['id']
    date = request.json['date']
    data = request.json['data']
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO duration_instance(duration_instance_time, duration_instance_date, duration_instance_duration_id) VALUES(%s, %s, %s);", (data, date, id))
    mysql.connection.commit()
    cursor.close()
    return "Added"

@app.route("/get-all-employees", methods=['GET'])
def get_all_employees():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT employees_id, employees_first_name, employees_last_name, employees_email, employees_permissions FROM employees")
    data = cursor.fetchall()
    cursor.close()
    return (jsonify(data))


@app.route("/delete-employee", methods=['POST'])
def delete_employee():
    id = request.json['id']
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM employees WHERE employees_id = %s", [id])
    cursor.connection.commit()
    cursor.close()
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * from employees")
    data = cursor.fetchall()
    cursor.close()
    return (jsonify(data))


@app.route("/edit-employee", methods=['PATCH'])
def edit_employee():
    id = request.json['id']
    firstname = request.json['firstname']
    lastname = request.json['lastname']
    email = request.json['email']
    password = request.json['password']
    hashed = bcrypt.hashpw(password.encode(encoding = "UTF-8"), bcrypt.gensalt())
    permissions = request.json['permissions']
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE employees SET employees_first_name = %s, employees_last_name = %s, employees_email = %s, employees_password= %s, employees_permissions = %s WHERE employees_id = %s;", (firstname, lastname, email, hashed, permissions, id))
    cursor.connection.commit()
    cursor.close()
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * from employees")
    data = cursor.fetchall()
    cursor.close()
    return (jsonify(data))


@app.route("/add-employee", methods=['POST'])
def add_employee():
    firstname = request.json['firstname']
    lastname = request.json['lastname']
    email = request.json['email']
    password = request.json['password']
    hashed = bcrypt.hashpw(password.encode(encoding = "UTF-8"), bcrypt.gensalt())
    permissions = request.json['permissions']
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO employees(employees_first_name, employees_last_name, employees_email, employees_password, employees_permissions) VALUES(%s, %s, %s, %s, %s);", (firstname, lastname, email, hashed, permissions))
    cursor.connection.commit()
    cursor.close()
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * from employees")
    data = cursor.fetchall()
    cursor.close()
    return (jsonify(data))

if __name__ == '__main__':
    app.run(debug=True)