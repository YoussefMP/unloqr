
OK_MSG = {"ID": 0, "text": "OK"}

SOMETHING_WENT_WRONG = {"ID": 97, "text": "Something went wrong while processing this request"}
NOT_VALID_EMAIL = {"ID": 99, "text": "this email address is not a valid one"}
EMAIL_NOT_CONFIRMED = {"ID": 105, "text": "Please confirm your email before proceeding"}


# Login handling messages
LOGIN_GRANTED = {"ID": 100, "text": "Success", "UID": "UID", "name": "name"}
LOGIN_DENIED = {"ID": 101, "text": "Failed to log in"}
USER_DOESNT_EXIST = {"ID": 103, "text": "This email is not registered"}

# Password change handling messages
PW_RESET_REQUEST_ACCEPTED = {"ID": 130, "text": "Email for password reset was sent."}
PW_RESET_REQUEST_DENIED = {"ID": 131, "text": "Request denied"}
PW_UPDATE_SUCCESSFUL = {"ID": 132, "text": "Your Password has been updated"}
PW_OLD_PASSWORD_WRONG = {"ID": 133, "text": "Typed old password is wrong"}

# Access requests handling messages
ACCESS_GRANTED = {"ID": 140, "text": "Access granted"}
ACESS_DENIED = {"ID": 141, "text": "Access denied"}
DENIED_ON_DEVICE = {"ID": 143, "text": "You are not allowed on this device"}

# Admin request messages
USERS_LIST = {"ID": 150, "users": "users"}
DEVICE_NOT_FOUND = {"ID": 151, "text": "This device Id is not in the database."}
USER_ADDED = {"ID": 152, "text": "user has been added to the database"}
USER_ADDED_TO_DEVICE = {"ID": 154, "text": "User has been added to the list of allowed users on this device"}
USER_DELETED = {"ID": 156, "text": "User has been removed from the database"}
