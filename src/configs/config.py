from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	BOT_TOKEN: str
	TEXT_MAX_LENGTH: int
	VK_API_VERSION: str
	BASE_URL: str
	VK_APP_SERVICE_KEY: str
	REDIS_HOST: str
	REDIS_PORT: int
	REDIS_DATABASE: int
	RMQ_HOST: str
	RMQ_PORT: int
	RMQ_USER: str
	RMQ_PASSWORD: str
	RMQ_ROUTING_KEY: str
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

