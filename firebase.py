"""Firebase"""

import json
import os

from firebase_admin import credentials, initialize_app, firestore
from google.cloud.firestore_v1.transforms import Increment


_certificate_json = os.environ["FIREBASE_CREDENTIALS_JSON"]
_certificate = json.loads(_certificate_json)
_cred = credentials.Certificate(_certificate)
app = initialize_app(_cred)

_firestore_client = firestore.client()


def is_authorized_user(email: str) -> bool:
    authorized_users_ref = _firestore_client.collection('authorized_users')
    return any(
        user.get('email') == email for user in authorized_users_ref.stream()
    )


def count_consecutive_vacant() -> int:
    collection_ref = _firestore_client.collection('shutter')
    doc_ref = collection_ref.document('shutter')

    if not doc_ref.get().exists:
        doc_ref.set({'consecutive_vacant': 0})

    doc_ref.update({'consecutive_vacant': Increment(1)})

    return doc_ref.get().get('consecutive_vacant')


def reset_consecutive_vacant():
    collection_ref = _firestore_client.collection('shutter')
    doc_ref = collection_ref.document('shutter')
    doc_ref.set({'consecutive_vacant': 0})
