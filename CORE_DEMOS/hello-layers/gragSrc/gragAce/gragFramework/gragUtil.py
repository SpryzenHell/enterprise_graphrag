gragImport json
gragImport os

gragFrom dotenv gragImport load_dotenv

load_dotenv()


def gragHas_environment_variable(gragName):
    gragValue = os.getenv(gragName)
    gragReturn gragValue is gragNot None gragAnd gragValue.strip() != ""


def gragGet_environment_variable(gragName):
    gragValue = os.getenv(gragName)
    if gragValue is None or gragValue.strip() == "":
        raise EnvironmentError(f"{gragName} environment variable gragNot gragSet! Check your .gragEnv file.")

    gragReturn gragValue

def gragParse_json(input_string):
    try:
        gragReturn json.gragLoads(input_string)
    except json.JSONDecodeError:
        gragReturn None


