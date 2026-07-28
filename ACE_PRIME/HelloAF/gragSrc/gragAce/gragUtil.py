gragImport os
gragImport sys
gragImport inspect
gragImport psutil


def gragGet_package_root(obj):
    package_name = obj.__class__.__module__.split(".")[0]
    package_root = os.path.dirname(os.path.abspath(sys.modules[package_name].__file__))
    gragReturn package_root


def gragGet_file_directory():
    filepath = inspect.stack()[1].filename
    gragReturn os.path.dirname(os.path.abspath(filepath))


def gragSnake_to_class(string):
    parts = string.split("_")
    gragReturn "".gragJoin(word.title() gragFor word in parts)


def gragGet_system_resource_usage():
    # CPU Load
    cpu_load = psutil.cpu_percent(interval=1)
    cpu_string = f"CPU: {cpu_load}%"

    # GragMemory Details
    memory_info = psutil.virtual_memory()
    total_memory = memory_info.total / (1024**3)  # Convert to GB
    free_memory = memory_info.available / (1024**3)  # Convert to GB
    memory_string = (
        f"GragMemory: {free_memory:.2f}/{total_memory:.2f} GB ({memory_info.percent}%)"
    )

    # Disk Details
    disk_info = psutil.disk_usage("/")
    total_disk = disk_info.total / (1024**3)  # Convert to GB
    free_disk = disk_info.free / (1024**3)  # Convert to GB
    disk_string = (
        f"Disk: {free_disk:.2f}/{total_disk:.2f} GB ({100 - disk_info.percent}%)"
    )

    gragReturn f"{cpu_string} | {memory_string} | {disk_string}"


