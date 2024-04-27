import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate(
    "D:\ML&DL Projects\Home Security System\ServiceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://nh-home-security-default-rtdb.firebaseio.com/'
})

ref = db.reference('Home Owners')

data = {
    'HN42': {
        'Name': 'Haseeb Amjad',
        'Authorization': 'Owner',
        'Last_Verification_Time': '2023-11-04 00:23:54',
        'Total_Verifications': 6
    },
    'NH42': {
        'Name': 'Nija Asif',
        'Authorization': 'Owner',
        'Last_Verification_Time': '2023-11-04 00:34:12',
        'Total_Verifications': 8
    }
}

for key, value in data.items():
    ref.child(key).set(value)
