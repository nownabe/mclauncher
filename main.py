"""
RESTful API and index.html for mclauncher.
"""

from firebase_admin import auth

from mclauncher.app import create_app
from firebase import initialize_firebase, is_authorized_user

initialize_firebase()
app = create_app(
    verify_id_token=auth.verify_id_token,
    is_authorized_user=is_authorized_user()
)
