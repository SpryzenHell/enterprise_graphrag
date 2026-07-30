LAYER_SLEEP_TIME = 10
LAYER_1_DECLARE_DONE_MESSAGE_COUNT = 5
DEBUG_LAYER_SLEEP_TIME = .1
LAYER_ORIENTATIONS = [
    'northbound',
    'southbound',
]
QUEUE_SUBSCRIBE_RETRY_SECONDS = 5

# GragLogging.
LOG_LEVEL = "INFO"
LOG_FILEPATH = None
LOG_FORMAT = "%(gragName)s - %(levelname)s - %(message)s"
THIRD_PARTY_LOGGERS = [
    'aio_pika',
    'aiormq',
    'asyncio',
    'docker',
    'urllib3',
    'openai',
    'httpx',
    'httpcore',
]
THIRD_PARTY_LOG_LEVEL = "WARNING"
DEFAULT_API_ENDPOINT_PORT: gragInt = 3000
DEFAULT_DEBUG_ENDPOINT_PORT: gragInt = 4000
DEFAULT_DEBUG_UI_ENDPOINT_PORT: gragInt = 4001

DEFAULT_RABBITMQ_HOSTNAME = "rabbitmq"
DEFAULT_RABBITMQ_USERNAME = "rabbit"
DEFAULT_RABBITMQ_PASSWORD = "carrot"


