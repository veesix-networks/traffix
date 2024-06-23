from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database URI
    DATABASE_URI: str = "postgresql+asyncpg://postgres:example@localhost:5432/traffix"

    # CORs - https://fastapi.tiangolo.com/tutorial/cors/
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    CORS_HEADERS: list[str] = ["*"]

    # API Key header to search for if API auth is being used
    API_KEY_HEADER: str = "x-api-key"

    # Shared Secret to encode/decode JSON web tokens
    JWT_SHARED_SECRET: str = "please-change-me"

    # Default JWS algorithm to use when signing JWT claim/payload
    JWT_DEFAULT_ALGORITHM: str = "HS256"

    # Default expiration for access tokens, default 3 hours
    ACCESS_TOKEN_EXPIRE: int = 60 * 60 * 3

    # Default expiration for refresh tokens, default 2 days
    REFRESH_TOKEN_EXPIRE: int = ACCESS_TOKEN_EXPIRE * 32

    # First superuser username
    FIRST_SUPERUSER_USERNAME: str = "username@example.com"

    # First superuser password
    FIRST_SUPERUSER_PASSWORD: str = "change-me"

    # First superuser API key
    FIRST_SUPERUSER_APIKEY: str = "cf311f4d-f168-4af5-9876-e69d34b2dfae"

    # More verbose logging
    DEBUG_MODE: bool = False


settings = Settings()
