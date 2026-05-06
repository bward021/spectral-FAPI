import os
import bcrypt
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.secret_key = os.environ.get('SECRET_KEY') or 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.permanent_session_lifetime = timedelta(hours=24)

db = SQLAlchemy(app)

# ── Models ──────────────────────────────────────────────────────────────────

class Employee(db.Model):
    __tablename__ = 'employees'
    employees_id = db.Column(db.Integer, primary_key=True)
    employees_first_name = db.Column(db.String(100))
    employees_last_name = db.Column(db.String(100))
    employees_email = db.Column(db.String(200), unique=True)
    employees_password = db.Column(db.LargeBinary)
    employees_permissions = db.Column(db.String(50))

class Client(db.Model):
    __tablename__ = 'client'
    client_id = db.Column(db.Integer, primary_key=True)
    client_firstname = db.Column(db.String(100))
    client_lastname = db.Column(db.String(100))
    client_age = db.Column(db.Integer)
    client_gender = db.Column(db.String(50))
    client_supervisor = db.Column(db.String(100))

class Address(db.Model):
    __tablename__ = 'addresses'
    addresses_id = db.Column(db.Integer, primary_key=True)
    addresses_one = db.Column(db.String(200))
    addresses_two = db.Column(db.String(200))
    addresses_city = db.Column(db.String(100))
    addresses_state = db.Column(db.String(50))
    addresses_postal_code = db.Column(db.String(20))
    addresses_client_id = db.Column(db.Integer, db.ForeignKey('client.client_id'))

class Trial(db.Model):
    __tablename__ = 'trial'
    trial_id = db.Column(db.Integer, primary_key=True)
    trial_name = db.Column(db.String(200))
    trial_category = db.Column(db.String(100))
    trial_description = db.Column(db.String(500))
    trial_client_id = db.Column(db.Integer, db.ForeignKey('client.client_id'))

class TrialInstance(db.Model):
    __tablename__ = 'trial_instance'
    trial_instance_id = db.Column(db.Integer, primary_key=True)
    trial_instance_correct = db.Column(db.Integer)
    trial_instance_prompted = db.Column(db.Integer)
    trial_instance_incorrect = db.Column(db.Integer)
    trial_instance_date = db.Column(db.String(50))
    trial_instance_trial_id = db.Column(db.Integer, db.ForeignKey('trial.trial_id'))

class Frequency(db.Model):
    __tablename__ = 'frequency'
    frequency_id = db.Column(db.Integer, primary_key=True)
    frequency_name = db.Column(db.String(200))
    frequency_description = db.Column(db.String(500))
    frequency_client_id = db.Column(db.Integer, db.ForeignKey('client.client_id'))

class FrequencyInstance(db.Model):
    __tablename__ = 'frequency_instance'
    frequency_instance_id = db.Column(db.Integer, primary_key=True)
    frequency_instance_data = db.Column(db.Integer)
    frequency_instance_date = db.Column(db.String(50))
    frequency_instance_frequency_id = db.Column(db.Integer, db.ForeignKey('frequency.frequency_id'))

class Duration(db.Model):
    __tablename__ = 'duration'
    duration_id = db.Column(db.Integer, primary_key=True)
    duration_name = db.Column(db.String(200))
    duration_description = db.Column(db.String(500))
    duration_client_id = db.Column(db.Integer, db.ForeignKey('client.client_id'))

class DurationInstance(db.Model):
    __tablename__ = 'duration_instance'
    duration_instance_id = db.Column(db.Integer, primary_key=True)
    duration_instance_time = db.Column(db.String(50))
    duration_instance_date = db.Column(db.String(50))
    duration_instance_duration_id = db.Column(db.Integer, db.ForeignKey('duration.duration_id'))

# ── Create Tables ────────────────────────────────────────────────────────────

with app.app_context():
    db.create_all()

# ── Auth Routes ──────────────────────────────────────────────────────────────

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']['username']
    password = request.json['password']['password']

    account = Employee.query.filter_by(employees_email=username).first()

    if account:
        if bcrypt.checkpw(password.encode('UTF-8'), account.employees_password):
            session.permanent = True
            session['id'] = account.employees_id
            return jsonify({"id": account.employees_id, "permissions": account.employees_permissions})
        else:
            return jsonify("Incorrect Username or Password"), 401
    else:
        return jsonify("Incorrect Username or Password"), 401

@app.route("/api/v1/logged-in", methods=["GET"])
def logged_in():
    if 'id' not in session or session['id'] == "0":
        return jsonify("No Cookie Set"), 401

    account = Employee.query.filter_by(employees_id=session['id']).first()
    if account:
        return jsonify({"employees_permissions": account.employees_permissions})
    return jsonify("No account Found"), 404

@app.route("/api/v1/logout", methods=["POST"])
def logout():
    session.pop("id", None)
    return jsonify("Logged out")

# ── Client Routes ────────────────────────────────────────────────────────────

@app.route('/clients', methods=['GET'])
def clients():
    all_clients = Client.query.all()
    return jsonify([{
        "client_id": c.client_id,
        "client_firstname": c.client_firstname,
        "client_lastname": c.client_lastname,
        "client_age": c.client_age,
        "client_gender": c.client_gender,
        "client_supervisor": c.client_supervisor
    } for c in all_clients])

@app.route('/clients/<id>', methods=['GET'])
def individual_client(id):
    c = Client.query.get(id)
    if c:
        return jsonify({
            "client_id": c.client_id,
            "client_firstname": c.client_firstname,
            "client_lastname": c.client_lastname,
            "client_age": c.client_age,
            "client_gender": c.client_gender,
            "client_supervisor": c.client_supervisor
        })
    return jsonify("Client not found"), 404

@app.route('/add-client', methods=['POST'])
def add_a_client():
    data = request.json
    new_client = Client(
        client_firstname=data['firstName'],
        client_lastname=data['lastName'],
        client_age=data['age'],
        client_gender=data['gender'],
        client_supervisor=data['supervisor']
    )
    db.session.add(new_client)
    db.session.commit()

    new_address = Address(
        addresses_one=data['addressOne'],
        addresses_two=data['addressTwo'],
        addresses_city=data['city'],
        addresses_state=data['st'],
        addresses_postal_code=data['postalCode'],
        addresses_client_id=new_client.client_id
    )
    db.session.add(new_address)
    db.session.commit()

    return jsonify("Client Added")

@app.route("/get-client-address/<id>", methods=['GET'])
def get_client_address(id):
    address = Address.query.filter_by(addresses_client_id=id).first()
    if address:
        return jsonify({
            "addresses_one": address.addresses_one,
            "addresses_two": address.addresses_two,
            "addresses_city": address.addresses_city,
            "addresses_state": address.addresses_state,
            "addresses_postal_code": address.addresses_postal_code
        })
    return jsonify("No address found"), 404

# ── Trial Routes ─────────────────────────────────────────────────────────────

@app.route("/add-client-trial/<id>", methods=['POST'])
def add_client_trial(id):
    data = request.json
    new_trial = Trial(
        trial_name=data['name'],
        trial_category=data['category'],
        trial_description=data['description'],
        trial_client_id=id
    )
    db.session.add(new_trial)
    db.session.commit()
    return jsonify("Added")

@app.route("/get-all-client-trials/<id>", methods=['GET'])
def get_all_client_trials(id):
    trials = Trial.query.filter_by(trial_client_id=id).all()
    return jsonify([{
        "trial_id": t.trial_id,
        "trial_name": t.trial_name,
        "trial_category": t.trial_category,
        "trial_description": t.trial_description
    } for t in trials])

@app.route("/check-trial-instance", methods=['GET'])
def check_trial_instance():
    date = request.args.get('date')
    id = request.args.get('id')
    if not date or not id:
        return jsonify("GET request is missing arguments"), 400

    instance = TrialInstance.query.filter_by(
        trial_instance_date=date,
        trial_instance_trial_id=id
    ).first()

    if instance:
        return jsonify({
            "trial_instance_id": instance.trial_instance_id,
            "trial_instance_correct": instance.trial_instance_correct,
            "trial_instance_prompted": instance.trial_instance_prompted,
            "trial_instance_incorrect": instance.trial_instance_incorrect
        })
    return jsonify("No data found"), 404

@app.route("/new-trial-instance", methods=['POST'])
def new_trial_instance():
    data = request.json
    new_instance = TrialInstance(
        trial_instance_correct=data['correct'],
        trial_instance_prompted=data['prompted'],
        trial_instance_incorrect=data['incorrect'],
        trial_instance_date=data['date'],
        trial_instance_trial_id=data['id']
    )
    db.session.add(new_instance)
    db.session.commit()
    return jsonify("Added")

@app.route("/update-trial-instance-incorrect", methods=['PATCH'])
def update_trial_instance_incorrect():
    data = request.json
    instance = TrialInstance.query.filter_by(
        trial_instance_trial_id=data['id'],
        trial_instance_date=data['date']
    ).first()
    if instance:
        instance.trial_instance_incorrect = data['data']
        db.session.commit()
    return jsonify("Updated")

@app.route("/update-trial-instance-prompted", methods=['PATCH'])
def update_trial_instance_prompted():
    data = request.json
    instance = TrialInstance.query.filter_by(
        trial_instance_trial_id=data['id'],
        trial_instance_date=data['date']
    ).first()
    if instance:
        instance.trial_instance_prompted = data['data']
        db.session.commit()
    return jsonify("Updated")

@app.route("/update-trial-instance-correct", methods=['PATCH'])
def update_trial_instance_correct():
    data = request.json
    instance = TrialInstance.query.filter_by(
        trial_instance_trial_id=data['id'],
        trial_instance_date=data['date']
    ).first()
    if instance:
        instance.trial_instance_correct = data['data']
        db.session.commit()
    return jsonify("Updated")

@app.route("/edit-trial/<id>", methods=['PATCH'])
def edit_trial(id):
    trial = Trial.query.filter_by(trial_id=id).first()
    if not trial:
        return jsonify("Trial not found"), 404
    
    data = request.get_json()
    trial.trial_name = data.get('name', trial.trial_name)
    trial.trial_category = data.get('category', trial.trial_category)
    trial.trial_description = data.get('description', trial.trial_description)
    
    db.session.commit()
    
    return jsonify({
        "trial_id": trial.trial_id,
        "trial_name": trial.trial_name,
        "trial_category": trial.trial_category,
        "trial_description": trial.trial_description
    })


@app.route("/delete-trial/<id>", methods=['DELETE'])
def delete_trial(id):
    trial = Trial.query.filter_by(trial_id=id).first()
    if not trial:
        return jsonify("Trial not found"), 404
    
    db.session.delete(trial)
    db.session.commit()
    
    return jsonify("Trial deleted")

# ── Frequency Routes ─────────────────────────────────────────────────────────

@app.route("/add-client-frequency/<id>", methods=['POST'])
def add_client_frequency(id):
    data = request.json
    new_frequency = Frequency(
        frequency_name=data['name'],
        frequency_description=data['description'],
        frequency_client_id=id
    )
    db.session.add(new_frequency)
    db.session.commit()
    return jsonify("Added")

@app.route("/get-frequency/<id>", methods=['GET'])
def get_frequency(id):
    frequencies = Frequency.query.filter_by(frequency_client_id=id).all()
    return jsonify([{
        "frequency_id": f.frequency_id,
        "frequency_name": f.frequency_name,
        "frequency_description": f.frequency_description
    } for f in frequencies])

@app.route("/get-frequency-instance", methods=['GET'])
def get_frequency_instance():
    date = request.args.get('date')
    id = request.args.get('id')
    if not date or not id:
        return jsonify("GET request is missing arguments"), 400

    instance = FrequencyInstance.query.filter_by(
        frequency_instance_date=date,
        frequency_instance_frequency_id=id
    ).first()

    if instance:
        return jsonify({
            "frequency_instance_id": instance.frequency_instance_id,
            "frequency_instance_data": instance.frequency_instance_data
        })
    return jsonify("No data found"), 404

@app.route("/new-frequency-instance", methods=['POST'])
def new_frequency_instance():
    data = request.json
    new_instance = FrequencyInstance(
        frequency_instance_data=data['data'],
        frequency_instance_date=data['date'],
        frequency_instance_frequency_id=data['id']
    )
    db.session.add(new_instance)
    db.session.commit()
    return jsonify("Added")

@app.route("/update-frequency-instance/<id>", methods=['PATCH'])
def update_frequency_instance(id):
    data = request.json
    instance = FrequencyInstance.query.filter_by(
        frequency_instance_frequency_id=id,
        frequency_instance_date=data['date']
    ).first()
    if instance:
        instance.frequency_instance_data = data['data']
        db.session.commit()
    return jsonify("Updated")

# ── Duration Routes ──────────────────────────────────────────────────────────

@app.route("/add-client-duration/<id>", methods=['POST'])
def add_client_duration(id):
    data = request.json
    new_duration = Duration(
        duration_name=data['name'],
        duration_description=data['description'],
        duration_client_id=id
    )
    db.session.add(new_duration)
    db.session.commit()
    return jsonify("Added")

@app.route("/get-all-client-duration/<id>", methods=['GET'])
def get_all_client_duration(id):
    durations = Duration.query.filter_by(duration_client_id=id).all()
    return jsonify([{
        "duration_id": d.duration_id,
        "duration_name": d.duration_name,
        "duration_description": d.duration_description
    } for d in durations])

@app.route("/new-duration-instance", methods=['POST'])
def new_duration_instance():
    data = request.json
    new_instance = DurationInstance(
        duration_instance_time=data['data'],
        duration_instance_date=data['date'],
        duration_instance_duration_id=data['id']
    )
    db.session.add(new_instance)
    db.session.commit()
    return jsonify("Added")

# ── Employee Routes ──────────────────────────────────────────────────────────

@app.route("/setup-admin", methods=['GET'])
def setup_admin():
    # Check if admin already exists
    existing = Employee.query.filter_by(employees_email="admin@spectral.com").first()
    if existing:
        return jsonify("Admin already exists"), 400
    
    hashed = bcrypt.hashpw("admin123".encode('UTF-8'), bcrypt.gensalt())
    new_employee = Employee(
        employees_first_name="Admin",
        employees_last_name="User",
        employees_email="admin@spectral.com",
        employees_password=hashed,
        employees_permissions="Admin"
    )
    db.session.add(new_employee)
    db.session.commit()
    return jsonify("Admin created successfully")

@app.route("/get-all-employees", methods=['GET'])
def get_all_employees():
    employees = Employee.query.all()
    return jsonify([{
        "employees_id": e.employees_id,
        "employees_first_name": e.employees_first_name,
        "employees_last_name": e.employees_last_name,
        "employees_email": e.employees_email,
        "employees_permissions": e.employees_permissions
    } for e in employees])

@app.route("/add-employee", methods=['POST'])
def add_employee():
    data = request.json
    hashed = bcrypt.hashpw(data['password'].encode('UTF-8'), bcrypt.gensalt())
    new_employee = Employee(
        employees_first_name=data['firstname'],
        employees_last_name=data['lastname'],
        employees_email=data['email'],
        employees_password=hashed,
        employees_permissions=data['permissions']
    )
    db.session.add(new_employee)
    db.session.commit()
    employees = Employee.query.all()
    return jsonify([{
        "employees_id": e.employees_id,
        "employees_first_name": e.employees_first_name,
        "employees_last_name": e.employees_last_name,
        "employees_email": e.employees_email,
        "employees_permissions": e.employees_permissions
    } for e in employees])

@app.route("/edit-employee", methods=['PATCH'])
def edit_employee():
    data = request.json
    employee = Employee.query.get(data['id'])
    if employee:
        hashed = bcrypt.hashpw(data['password'].encode('UTF-8'), bcrypt.gensalt())
        employee.employees_first_name = data['firstname']
        employee.employees_last_name = data['lastname']
        employee.employees_email = data['email']
        employee.employees_password = hashed
        employee.employees_permissions = data['permissions']
        db.session.commit()
    employees = Employee.query.all()
    return jsonify([{
        "employees_id": e.employees_id,
        "employees_first_name": e.employees_first_name,
        "employees_last_name": e.employees_last_name,
        "employees_email": e.employees_email,
        "employees_permissions": e.employees_permissions
    } for e in employees])

@app.route("/delete-employee", methods=['DELETE'])
def delete_employee():
    data = request.json
    employee = Employee.query.get(data['id'])
    if employee:
        db.session.delete(employee)
        db.session.commit()
    employees = Employee.query.all()
    return jsonify([{
        "employees_id": e.employees_id,
        "employees_first_name": e.employees_first_name,
        "employees_last_name": e.employees_last_name,
        "employees_email": e.employees_email,
        "employees_permissions": e.employees_permissions
    } for e in employees])

# ── Graph Route ──────────────────────────────────────────────────────────────

@app.route("/client/frequency-graph/<id>")
def collect_data_for_frequency_graph(id):
    frequency = Frequency.query.filter_by(frequency_client_id=id).order_by(Frequency.frequency_id.desc()).first()
    if not frequency:
        return jsonify("no frequency found"), 404

    instances = FrequencyInstance.query.filter_by(
        frequency_instance_frequency_id=frequency.frequency_id
    ).order_by(FrequencyInstance.frequency_instance_id.desc()).limit(4).all()

    return jsonify([{
        "frequency_instance_data": i.frequency_instance_data,
        "frequency_instance_date": i.frequency_instance_date
    } for i in instances])

if __name__ == '__main__':
    app.run(debug=True)