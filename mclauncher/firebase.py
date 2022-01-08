'''Firebase client for mclauncher'''


import json
from typing import Any
from firebase_admin import initialize_app, credentials, firestore, auth
from google.cloud.firestore_v1 import transforms

from mclauncher.config import Config


class Firebase:
    __AUTHORIZED_USERS_COLLECTION = 'authorized_users'
    __SHUTTER_COLLECTION = 'shutter'
    __SHUTTER_DOCUMENT = 'shutter'
    __SHUTTER_VACANT_STREAK_KEY = 'vacant_streak'

    def __init__(self, config: Config):
        if config.firebase_credentials_json is None:
            initialize_app(options={'project_id': 'project-id'})
        else:
            credential = credentials.Certificate(json.loads(config.firebase_credentials_json))
            initialize_app(credential=credential)

        self.__firestore = firestore.client()

    def is_authorized_user(self, email: str) -> bool:
        doc_ref = self.__firestore.collection(
            self.__AUTHORIZED_USERS_COLLECTION
        )
        return any(user.get('email') == email for user in doc_ref.stream())

    def count_consecutive_vacant(self) -> int:
        collection_ref = self.__firestore.collection(self.__SHUTTER_COLLECTION)
        doc_ref = collection_ref.document(self.__SHUTTER_DOCUMENT)

        if not doc_ref.get().exists:
            self.reset_consecutive_vacant()

        doc_ref.update({self.__SHUTTER_VACANT_STREAK_KEY: transforms.Increment(1)})

        return doc_ref.get().get(self.__SHUTTER_VACANT_STREAK_KEY)

    def reset_consecutive_vacant(self) -> None:
        collection_ref = self.__firestore.collection(self.__SHUTTER_COLLECTION)
        doc_ref = collection_ref.document(self.__SHUTTER_DOCUMENT)
        doc_ref.set({self.__SHUTTER_VACANT_STREAK_KEY: 0})

    def verify_id_token(self, id_token: str) -> Any:
        return auth.verify_id_token(id_token)
