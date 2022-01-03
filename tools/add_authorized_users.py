import json
import os
from sys import argv

from firebase_admin import credentials, initialize_app, firestore

email = argv[1]

certificate_json = os.environ["FIREBASE_CREDENTIALS_JSON"]
certificate = json.loads(certificate_json)
cred = credentials.Certificate(certificate)
initialize_app(cred)

firestore_database = firestore.client()

firestore_database.collection('authorized_users').add({'email': email})
