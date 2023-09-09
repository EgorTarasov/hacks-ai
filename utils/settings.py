from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    tg_token: str = Field(..., alias="TG_TOKEN")
    sqlite_filepath: str = Field("data.sqlite", alias="SQLITE_PATH")
    ml_train: str = Field("ml/train.csv")
    ml_embeds: str = Field("ml/embeds.pkl")

settings = Settings(_env_file=".env")