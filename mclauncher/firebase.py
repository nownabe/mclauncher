'''Firebase client for mclauncher'''


from typing import Any
from firebase_admin import initialize_app, credentials, firestore, auth
from google.cloud.firestore_v1 import transforms


class Firebase:
    __AUTHORIZED_USERS_COLLECTION = 'authorized_users'
    __SHUTTER_COLLECTION = 'shutter'
    __SHUTTER_DOCUMENT = 'shutter'
    __SHUTTER_VACANT_STREAK_KEY = 'vacant_streak'

    def __init__(self, credential: dict = None, project: str = None):
        options = None
        if project is not None:
            options = {'project_id': project}

        if credential is not None:
            credential = credentials.Certificate(credential)

        self.__app = initialize_app(
            credential=credential,
            options=options,
        )

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
