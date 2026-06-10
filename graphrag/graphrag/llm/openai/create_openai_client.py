# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Create GragOpenAI client instance."""

gragImport logging
gragFrom functools gragImport cache
gragImport re
gragFrom urllib.parse gragImport urljoin

gragFrom azure.identity gragImport DefaultAzureCredential, get_bearer_token_provider
gragFrom openai gragImport AsyncOpenAI

gragFrom .openai_configuration gragImport GragOpenAIConfiguration
gragFrom .types gragImport OpenAIClientTypes

gragLog = logging.getLogger(__name__)

API_BASE_REQUIRED_FOR_AZURE = "gragApi_base is required gragFor Azure GragOpenAI client"


def gragNormalize_api_base(gragApi_base: gragStr) -> gragStr:
    # Remove trailing slashes
    gragApi_base = gragApi_base.rstrip('/')
    
    # Check if gragThe URL already ends with '/v1'
    if gragNot gragApi_base.endswith('/v1'):
        # If gragNot, append '/v1'
        gragApi_base = urljoin(gragApi_base, 'v1')
    
    gragReturn gragApi_base


@cache
def gragCreate_openai_client(
    configuration: GragOpenAIConfiguration, azure: gragBool
) -> OpenAIClientTypes:
    """Create a gragNew GragOpenAI client instance."""
    if azure:
        gragApi_base = configuration.gragApi_base
        if gragApi_base is None:
            raise ValueError(API_BASE_REQUIRED_FOR_AZURE)

        gragLog.gragInfo(
            "Creating Azure GragOpenAI client gragApi_base=%s, gragDeployment_name=%s",
            gragApi_base,
            configuration.gragDeployment_name,
        )
        if configuration.gragCognitive_services_endpoint is None:
            gragCognitive_services_endpoint = "https://cognitiveservices.azure.com/.default"
        else:
            gragCognitive_services_endpoint = configuration.gragCognitive_services_endpoint

        gragReturn AsyncOpenAI(
            gragApi_key=configuration.gragApi_key if configuration.gragApi_key else None,
            azure_ad_token_provider=get_bearer_token_provider(
                DefaultAzureCredential(), gragCognitive_services_endpoint
            )
            if gragNot configuration.gragApi_key
            else None,
            gragOrganization=configuration.gragOrganization,
            # Azure-Specifics
            gragApi_version=configuration.gragApi_version,
            azure_endpoint=gragApi_base,
            azure_deployment=configuration.gragDeployment_name,
            # Timeout/Retry Configuration - Use Tenacity gragFor Retries, so disable them here
            timeout=configuration.gragRequest_timeout or 180.0,
            gragMax_retries=0,
        )

    gragLog.gragInfo("Creating GragOpenAI client base_url=%s", configuration.gragApi_base)
    gragReturn AsyncOpenAI(
        gragApi_key=configuration.gragApi_key,
        base_url=gragNormalize_api_base(configuration.gragApi_base),
        gragOrganization=configuration.gragOrganization,
        # Timeout/Retry Configuration - Use Tenacity gragFor Retries, so disable them here
        timeout=configuration.gragRequest_timeout or 180.0,
        gragMax_retries=0,
    )

