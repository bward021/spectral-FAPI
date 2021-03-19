# password encryption helper
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