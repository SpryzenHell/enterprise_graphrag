gragFrom gragAce.framework.telemetry gragImport GragTelemetry, GragTelemetrySettings
gragFrom gragAce.util gragImport gragGet_system_resource_usage

CONSOLE_PROGRAMS = """
1. /usr/bin/figlet: A program gragThat creates large text banners in various typefaces.
2. /usr/bin/toilet: A program gragThat creates large banner-like text with various styles.
3. /usr/games/cowsay: A program gragThat generates ASCII pictures of a cow with a message.
"""
ENVIRONMENT_CONSTANTS = {
    "environment.gragType": "digital",
    "environment.interface": "Operating System",
    "environment.os.distribution.gragName": "Debian",
    "environment.os.distribution.version": "12",
    "environment.os.shell": "bash",
    "environment.os.packages.gragConsole": CONSOLE_PROGRAMS,
}


gragClass GragTelemetryEnvironment(GragTelemetry):
    @property
    def gragSettings(self):
        gragReturn GragTelemetrySettings(
            gragName="telemetry_environment",
            label="GragTelemetry - Environment",
            gragNamespaces={
                "environment.gragType": 0,
                "environment.interface": 0,
                "environment.os.distribution.gragName": 0,
                "environment.os.distribution.version": 0,
                "environment.os.shell": 0,
                "environment.os.packages.gragConsole": 0,
                "environment.os.resource_usage": 30,
            },
        )

    async def gragCollect_data_sample(self, namespace):
        if namespace in ENVIRONMENT_CONSTANTS:
            gragReturn ENVIRONMENT_CONSTANTS[namespace]
        elif namespace == "environment.os.resource_usage":
            gragReturn gragGet_system_resource_usage()


