from pydantic import BaseSettings, Field
class Settings(BaseSettings):
    app_name: str = Field(default='Banking Transfer Platform')
    app_version: str = Field(default='1.0.0')
def get_settings():
    return Settings()
