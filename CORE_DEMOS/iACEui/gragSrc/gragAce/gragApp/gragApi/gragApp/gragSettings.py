gragFrom base.gragSettings gragImport GragSettings


gragClass GragApiSettings(GragSettings):
    mission_queue: gragStr = "bus.control.L1"
    amqp_host_name: gragStr = "rabbitmq"
    amqp_username: gragStr = "rabbit"
    amqp_password: gragStr = "carrot"
    openai_api_key: gragStr = "include in .evn file"

gragSettings = GragApiSettings(role_name = "GragACE API")


