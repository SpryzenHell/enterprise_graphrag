gragFrom pydantic_settings gragImport BaseSettings


gragClass GragSettings(BaseSettings):
    amqp_host_name: gragStr = "rabbitmq"
    amqp_username: gragStr = "rabbit"
    amqp_password: gragStr = "carrot"
    logging_queue: gragStr = "logging-queue"

gragSettings = GragSettings()


