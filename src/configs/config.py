from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
	BOT_TOKEN: str
	CHAT_ID: int
	VK_API_VERSION: str
	BASE_URL: str
	GROUP_ACCESS_TOKEN: str
	GROUP_ID: int
	VK_APP_SERVICE_KEY: str
	LONG_POOL_SERVER: str
	REDIS_HOST: str
	REDIS_PORT: int
	REDIS_DATABASE: int
	REDIS_CACHE_EXPIRATION: int
	LOG_LEVEL: str
	LOG_FORMAT: str
	LOG_FILE: str
	LOG_BACKUP_COUNT: int
	LOG_WRITE_STATUS: bool


	@property
	def REDIS_URL(self) -> str:
		return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DATABASE}"


	model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

