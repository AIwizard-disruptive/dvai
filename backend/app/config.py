"""Application configuration using Pydantic Settings."""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "Meeting Intelligence Platform"
    env: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    supabase_jwt_secret: str
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Security
    encryption_key: str  # 32-byte base64-encoded key
    
    # CORS
    cors_origins: str = "http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    # Transcription Providers
    klang_api_key: str = ""
    klang_api_url: str = "https://api.klang.ai/v1"
    
    mistral_api_key: str = ""
    mistral_api_url: str = "https://api.mistral.ai/v1"
    
    openai_api_key: str = ""
    openai_org_id: str = ""
    
    default_transcription_provider: str = "klang"
    
    # Linear (API key for global/testing)
    linear_api_key: str = ""
    linear_api_url: str = "https://api.linear.app/graphql"
    
    # Linear OAuth (for user-level integrations)
    linear_oauth_client_id: str = ""
    linear_oauth_client_secret: str = ""
    linear_oauth_redirect_uri: str = "http://localhost:8000/user-integrations/linear/callback"
    
    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/integrations/google/callback"
    
    # Feature Flags
    enable_email_send: bool = False
    enable_calendar_booking: bool = False
    
    # Slack
    slack_webhook_url: str = ""
    
    # Storage
    supabase_storage_bucket: str = "artifacts"
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # Sentry
    sentry_dsn: str = ""
    
    # Pipedrive CRM
    pipedrive_api_token: str = ""
    pipedrive_api_url: str = "https://api.pipedrive.com/v1"
    pipedrive_company_domain: str = ""  # e.g., "yourcompany.pipedrive.com"
    
    # Fortnox Accounting
    fortnox_api_token: str = ""
    fortnox_client_secret: str = ""
    fortnox_api_url: str = "https://api.fortnox.se/3"


# Global settings instance
settings = Settings()


