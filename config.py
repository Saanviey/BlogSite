from pydantic import SecretStr
from pydantic_settings import BaseSettings , SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    max_upload_size_bytes:int =5* 1024 * 1024
    posts_per_page:int =10

    reset_token_expire_minutes:int = 60
    brevo_api_key: str
    mail_from: str
    
    frontend_url: str = "http://localhost:8000"

    database_url:str

    # S3 Configuration
    s3_bucket_name: str
    s3_region: str = "us-east-1"
    s3_access_key_id: SecretStr | None = None
    s3_secret_access_key: SecretStr | None = None
    s3_endpoint_url: str | None = None



settings = Settings()




