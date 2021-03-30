# Spectral App Back-End

> Welcome to my Capstone Project! :) This project was built with the intent to collect and store data on clients who have Autism. it is an interactive app that allows for full CRUD.

> If you would like to check it out you can log in with the following credentials at [https://bw-spectral-rfe.netlify.app/clients]: 

  - Email: Visitor@spectral.com
  - Password: visitor321

> List of used technologies:

  - Flask - [https://flask.palletsprojects.com/en/1.1.x/]
  - Flask-mysqldb - [https://flask-mysqldb.readthedocs.io/en/latest/]
  - mysqlclient - [https://mysqlclient.readthedocs.io/]
  - Flask-Cors - [https://flask-cors.readthedocs.io/en/latest/]
  - datetime - [https://docs.python.org/3/library/datetime.html]
  - bcrypt - [https://github.com/pyca/bcrypt/]

> example of bcrypt used in code:

```
# >>> import bcrypt
# >>> password = b"super secret password"
# >>> # Hash a password for the first time, with a randomly-generated salt
# >>> hashed = bcrypt.hashpw(password, bcrypt.gensalt())
# >>> # Check that an unhashed password matches one that has previously been
# >>> # hashed
# >>> if bcrypt.checkpw(password, hashed):
# ...     print("It Matches!")
# ... else:
# ...     print("It Does not Match :(")
# import bcrypt
# password = "Whatever"
# print(password.encode(encoding = "UTF-8"))
# hashed = bcrypt.hashpw(password.encode(encoding = "UTF-8"), bcrypt.gensalt())
# print(hashed)
```