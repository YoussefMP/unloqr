
OK_MSG = {"ID": 0, "text": "OK"}

SOMETHING_WENT_WRONG = {"ID": 97, "text": "Bei der Bearbeitung dieser Anfrage ist ein Fehler aufgetreten"}
NOT_VALID_EMAIL = {"ID": 99, "text": "Die eingegebene E-Mail-Adresse ist ungültig"}
EMAIL_NOT_CONFIRMED = {"ID": 105, "text": "Bitte bestätigen Sie Ihre E-Mail, bevor Sie fortfahren"}


# Login handling messages
LOGIN_GRANTED = {"ID": 100, "text": "Erfolgreich eingeloggt", "UID": "UID", "name": "name"}
LOGIN_DENIED = {"ID": 101, "text": "Anmeldung fehlgeschlagen"}
USER_DOESNT_EXIST = {"ID": 103, "text": "Die E-Mail-Adresse ist nicht registriert"}

# Password change handling messages
PW_RESET_REQUEST_ACCEPTED = {"ID": 130, "text": "E-Mail zum Zurücksetzen des Passworts wurde gesendet."}
PW_RESET_REQUEST_DENIED = {"ID": 131, "text": "Antrag abgelehnt"}
PW_UPDATE_SUCCESSFUL = {"ID": 132, "text": "Ihr Passwort wurde aktualisiert"}
PW_OLD_PASSWORD_WRONG = {"ID": 133, "text": "Das eingegebene alte Passwort ist falsch"}

# Access requests handling messages
ACCESS_GRANTED = {"ID": 140, "text": "Zugang gewährt", "uid": "uid", "did": "did", "date": "date"}
ACESS_DENIED = {"ID": 141, "text": "Zugang verweigert"}
DENIED_ON_DEVICE = {"ID": 143, "text": "Sie sind für dieses Gerät nicht zugelassen"}
DEVICE_OFFLINE = {"ID": 145, "text": "Gerät ist offline"}
FILE_GOT = {"ID": 146, "text": "File Got"}

# Admin request messages
USERS_LIST = {"ID": 150, "users": "users"}
DEVICE_NOT_FOUND = {"ID": 151, "text": "Das Geräte-ID ist nicht in der Datenbank enthalten."}
USER_ADDED = {"ID": 152, "text": "Benutzer wurde der Datenbank hinzugefügt"}
USER_ADDED_TO_DEVICE = {"ID": 154, "text": "Der Benutzer wurde zur Liste der zugelassenen Benutzer auf diesem Gerät hinzugefügt"}
USER_DELETED = {"ID": 156, "text": "Benutzer wurde aus der Datenbank entfernt"}
