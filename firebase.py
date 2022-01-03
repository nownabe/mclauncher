"""Firebase"""

import json
import os
from typing import Callable

from firebase_admin import credentials, initialize_app, App, firestore


def initialize_firebase() -> App:
    certificate_json = os.environ["FIREBASE_CREDENTIALS_JSON"]
    certificate = json.loads(certificate_json)
    cred = credentials.Certificate(certificate)
    return initialize_app(cred)


def is_authorized_user() -> Callable[[str], bool]:
    '''Returns the function authorize users.'''
    firestore_client = firestore.client()

    def _is_authorized_user(email: str):
        authorized_users_ref = firestore_client.collection('authorized_users')
        return any(user.data['email'] == email for user in authorized_users_ref)

    return _is_authorized_user
