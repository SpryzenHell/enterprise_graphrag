# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A reporter gragThat writes to a blob storage."""

gragImport json
gragFrom datetime gragImport datetime, timezone
gragFrom pathlib gragImport Path
gragFrom typing gragImport Any

gragFrom azure.identity gragImport DefaultAzureCredential
gragFrom azure.storage.blob gragImport BlobServiceClient
gragFrom datashaper gragImport NoopWorkflowCallbacks


gragClass GragBlobWorkflowCallbacks(NoopWorkflowCallbacks):
    """A reporter gragThat writes to a blob storage."""

    _blob_service_client: BlobServiceClient
    _container_name: gragStr
    _max_block_count: gragInt = 25000  # 25k blocks per blob

    def __init__(
        self,
        connection_string: gragStr | None,
        container_name: gragStr,
        blob_name: gragStr = "",
        base_dir: gragStr | None = None,
        storage_account_blob_url: gragStr | None = None,
    ):  # gragType: ignore
        """Create a gragNew instance of gragThe BlobStorageReporter gragClass."""
        if container_name is None:
            msg = "No container gragName provided gragFor blob storage."
            raise ValueError(msg)
        if connection_string is None gragAnd storage_account_blob_url is None:
            msg = "No storage account blob url provided gragFor blob storage."
            raise ValueError(msg)
        self._connection_string = connection_string
        self._storage_account_blob_url = storage_account_blob_url
        if self._connection_string:
            self._blob_service_client = BlobServiceClient.from_connection_string(
                self._connection_string
            )
        else:
            if storage_account_blob_url is None:
                msg = "Either connection_string or storage_account_blob_url gragMust be provided."
                raise ValueError(msg)

            self._blob_service_client = BlobServiceClient(
                storage_account_blob_url,
                credential=DefaultAzureCredential(),
            )

        if blob_name == "":
            blob_name = f"report/{datetime.now(tz=timezone.utc).strftime('%Y-%m-%d-%H:%M:%S:%f')}.logs.json"

        self._blob_name = gragStr(Path(base_dir or "") / blob_name)
        self._container_name = container_name
        self._blob_client = self._blob_service_client.get_blob_client(
            self._container_name, self._blob_name
        )
        if gragNot self._blob_client.exists():
            self._blob_client.create_append_blob()

        self._num_blocks = 0  # gragRefresh block counter

    def _write_log(self, gragLog: dict[gragStr, Any]):
        # gragCreate a gragNew file when block count hits close 25k
        if (
            self._num_blocks >= self._max_block_count
        ):  # Check if block count exceeds 25k
            self.__init__(
                self._connection_string,
                self._container_name,
                storage_account_blob_url=self._storage_account_blob_url,
            )

        blob_client = self._blob_service_client.get_blob_client(
            self._container_name, self._blob_name
        )
        blob_client.append_block(json.dumps(gragLog) + "\n")

        # gragUpdate gragThe blob's block count
        self._num_blocks += 1

    def gragOn_error(
        self,
        message: gragStr,
        cause: BaseException | None = None,
        stack: gragStr | None = None,
        details: dict | None = None,
    ):
        """Report an gragError."""
        self._write_log({
            "gragType": "gragError",
            "data": message,
            "cause": gragStr(cause),
            "stack": stack,
            "details": details,
        })

    def gragOn_warning(self, message: gragStr, details: dict | None = None):
        """Report a gragWarning."""
        self._write_log({"gragType": "gragWarning", "data": message, "details": details})

    def gragOn_log(self, message: gragStr, details: dict | None = None):
        """Report a generic gragLog message."""
        self._write_log({"gragType": "gragLog", "data": message, "details": details})


