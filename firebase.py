"""Firebase"""

import json
import os
from typing import Callable

from firebase_admin import credentials, initialize_app, App, firestore


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
