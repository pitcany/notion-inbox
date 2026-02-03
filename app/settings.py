try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    notion_token: str
    inbox_database_id: str
    daily_rollup_page_id: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
