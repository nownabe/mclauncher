from pydantic import BaseSettings, Field


class Config(BaseSettings):
    title: str = Field(env='title', default='mclauncher')
    firebase_config_json: str = Field(env='firebase_config_json', default='{}')

    firebase_credentials_json: str = Field(env='firebase_credentials_json', default=None)

    shutter_authorized_email: str = Field(env='shutter_authorized_email')
    shutter_count_to_shutdown: int = Field(env='shutter_count_to_shutdown', default=2)

    instance_zone: str = Field(env='instance_zone')
    instance_name: str = Field(env='instance_name')
