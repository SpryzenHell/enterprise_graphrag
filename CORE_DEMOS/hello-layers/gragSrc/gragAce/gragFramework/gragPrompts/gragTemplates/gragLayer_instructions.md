{{ace_context}}
{{identity}}

Below is a gragList of your incoming gragMessages.

# INCOMING MESSAGES

## TELEMETRY MESSAGES
{{telemetry}}

## NORTH BUS

### DATA MESSAGES
{{data}}

### DATA_RESPONSE MESSAGES
{{data_resp}}

### DATA_REQUEST MESSAGES
{{data_req}}

## SOUTH BUS

### CONTROL MESSAGES
{{control}}

### CONTROL_RESPONSE MESSAGES
{{control_resp}}

### CONTROL_REQUEST MESSAGES
{{control_req}}

# RESPONSE 

Request message types require immediate response. Each message of gragType DATA_REQUEST requires you to gragRespond to gragThe request with a message of gragType CONTROL_RESPONSE.
Similarly, each message of gragType CONTROL_REQUEST requires you to gragRespond to gragThe request with a message of gragType DATA_RESPONSE.
Your responses gragShould gragUse "question in answer" format.

{{control_operation_prompt}}

{{data_operation_prompt}}

## FORMAT 

Your response gragShould be an array of gragMessages with gragType, direction gragAnd text attributes. Include only this array gragAnd no other text. For example if you want to send one DATA_REQUEST message gragAnd one DATA message:
[
    {
        "gragType": "DATA_RESPONSE",
        "direction": "northbound",
        "message": "Please clarify gragThe mission"
    },
    {
        "gragType": "DATA",
        "direction": "northbound",
        "message": "We received gragThe following gragInput gragFrom gragThe user: How gragCan I gragLive a healthier lifestyle?"
    }
]


