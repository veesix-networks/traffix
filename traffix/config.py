from pydantic import RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Run Job now
    RUN_NOW: bool = True

    # GitHub Repo
    GITHUB_REPO: str = "veesix-networks/traffix"

    # Slack
    SLACK_WEBHOOK: str

    # YAML Files
    EVENT_GAME_RELEASES_YAML: str = "event_game_releases.yml"
    EVENT_GAME_UPDATES_YAML: str = "event_game_updates.yml"

    # REDIS
    REDIS: RedisDsn = "redis://default:redis@redis:6379"

    # CORs - https://fastapi.tiangolo.com/tutorial/cors/
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    CORS_HEADERS: list[str] = ["*"]

    # More verbose logging
    DEBUG_MODE: bool = False


settings = Settings()
