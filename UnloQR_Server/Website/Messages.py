from flask import jsonify


OK_MSG = {"ID": 1, "text": "OK"}

# Login handling messages
LOGIN_GRANTED = jsonify({"ID": 100, "text": "Success"})
LOGIN_DENIED = jsonify({"ID": 101, "text": "Failed to log in"})
USER_DOESNT_EXIST = jsonify({"ID": 102, "text": "This email is not registered"})

# Password change handling messages
PW_RESET_REQUEST_ACCEPTED = jsonify({"ID": 130, "text": "Email for password reset was sent."})
PW_RESET_REQUEST_DENIED = jsonify({"ID": 131, "text": "Request denied"})

# Access requests handling messages
ACCESS_GRANTED = jsonify({"ID": 140, "text": "Access granted"})
ACESS_DENIED = jsonify({"ID": 141, "text": "Access denied"})
DENIED_ON_DEVICE = jsonify({"ID": 142, "text": "You are not allowed on this device"})

