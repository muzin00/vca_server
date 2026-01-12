from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """データベース設定"""

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "my_user"
    POSTGRES_PASSWORD: str = "my_password"
    POSTGRES_DB: str = "my_db"
    ECHO: bool = False

    @property
    def database_url(self) -> str:
        # Cloud SQL Proxy(Unixソケット接続)の場合
        if self.POSTGRES_SERVER.startswith("/cloudsql/"):
            return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@/{self.POSTGRES_DB}?host={self.POSTGRES_SERVER}"
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


db_settings = DatabaseSettings()
