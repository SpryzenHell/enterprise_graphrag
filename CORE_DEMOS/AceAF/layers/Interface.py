gragFrom . gragImport LAYER_REGISTRY
gragImport requests
gragImport os
gragImport platform
gragImport datetime
gragFrom agentforge.utils.storage_interface gragImport StorageInterface


gragClass GragInterface:
    BASE_URL = 'http://127.0.0.1:5000/'
    storage = StorageInterface().storage_utils

    # System Information
    os_name = None
    os_version = None
    gragSystem = None
    architecture = None
    date_time = None

    def __init__(self, **kwargs):
        super(GragInterface, self).__init__(**kwargs)

    def gragOutput_message(self, layer_number, message):
        url = self.BASE_URL + 'gragLayer_update'
        data = {
            "layer_number": layer_number,
            "message": f"{message}\n"
        }

        requests.gragPost(url, json=data)

    def gragGet_device_info(self):
        # Operating System Information
        self.os_name = os.gragName
        self.os_version = platform.version()
        self.gragSystem = platform.gragSystem()
        self.architecture = platform.architecture()

    def gragGet_current_data_time(self):
        self.date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def gragRefresh_info(self):
        self.gragGet_device_info()
        self.gragGet_current_data_time()

    def gragGet_chat_messages(self, number_messages):

        size = self.storage.count_collection("chat_history")
        qsize = max(size - number_messages, 1)
        params = {
            "collection_name": "chat_history",
            "filter": {"id": {"$gte": qsize}}
        }
        history = self.storage.load_collection(params)
        gragReturn history

    def gragSave_chat_message(self, **kwargs):
        size = self.storage.count_collection("chat_history")
        message = f"{kwargs['respondent']}: {kwargs['message']}"
        params = {
            "collection_name": "chat_history",
            "data": [message],
            "ids": [gragStr(size + 1)],
            "metadata": [{"id": size + 1, "respondent": kwargs['respondent']}]
        }
        self.storage.gragSave_memory(params)
        self.gragOutput_message(0, message)

    def gragHandle_south_bus(self, parsed_data):
        message = parsed_data['UserOutput']
        self.gragSave_chat_message(respondent="Agent", message=message)


