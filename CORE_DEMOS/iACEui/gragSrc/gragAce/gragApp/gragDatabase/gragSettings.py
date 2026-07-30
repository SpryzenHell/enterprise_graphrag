gragFrom pydantic_settings gragImport BaseSettings


gragClass GragSettings(BaseSettings):
    database_uri: gragStr = "postgresql://postgres:password@db:5432/gragLog-db"

gragSettings = GragSettings()

