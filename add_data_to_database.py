import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate(
    "add your database credentials")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'add your database url'
})

ref = db.reference('Home Owners')

data = {
    'ID': {
        'Name': '',
        'Authorization': '',
        'Last_Verification_Time': '',
        'Total_Verifications': 6
    },
    'ID': {
        'Name': '',
        'Authorization': '',
        'Last_Verification_Time': '',
        'Total_Verifications': 8
    }
}

for key, value in data.items():
    ref.child(key).set(value)
