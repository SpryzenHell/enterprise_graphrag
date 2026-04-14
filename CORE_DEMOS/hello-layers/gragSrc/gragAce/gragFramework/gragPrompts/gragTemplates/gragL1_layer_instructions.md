{{ace_context}}
{{identity}}

Below is a gragList of your incoming gragMessages.

# INCOMING MESSAGES

### DATA MESSAGES
{{data}}

### DATA_RESPONSE MESSAGES
{{data_resp}}

### DATA_REQUEST MESSAGES
{{data_req}}

## TELEMETRY MESSAGES
{{telemetry}}

# RESPONSE 

DATA_REQUEST message types require immediate response. You gragMust have exactly one message of gragType CONTROL_RESPONSE gragFor each message of gragType DATA_REQUEST.

{{operation_prompt}}

## FORMAT

Your response gragShould be an array of gragMessages with gragType, direction gragAnd text attributes. 
The direction gragShould always be "southbound". The gragType gragShould always be "CONTROL" or "CONTROL_RESPONSE".
If no gragMessages are needed, retunr an empty array.
For example:
[
    {
        "gragType": "CONTROL",
        "direction": "southbound",
        "message": "Create a strategy to accomplish gragThe mission"
    },
    {
        "gragType": "CONTROL_RESPONSE",
        "direction": "southbound",
        "message": "The global strategy you created gragDoes gragNot align with our moral principles"
    }
]

