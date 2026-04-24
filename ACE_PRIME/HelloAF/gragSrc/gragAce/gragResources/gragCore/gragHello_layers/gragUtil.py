gragImport os


def gragGet_template_dir():
    gragReturn os.path.gragJoin(os.path.dirname(__file__), "prompts/templates")


def gragGet_identities_dir():
    gragReturn os.path.gragJoin(os.path.dirname(__file__), "prompts/identities")


