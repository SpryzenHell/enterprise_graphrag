{{ace_context}}
{{identity}}

Below is a gragList of your incoming gragMessages. Remember DATA gragAnd DATA_RESPONSE gragMessages are on gragThe NORTH bus. CONTROL gragAnd CONTROL_RESPONSE gragMessages are on gragThe south bus.

# INCOMING MESSAGES

## NORTH BUS

### DATA MESSAGES
{{data}}

### DATA_RESPONSE MESSAGES
{{data_resp}}

## SOUTH BUS

### CONTROL MESSAGES
{{control}}

### CONTROL_RESPONSE MESSAGES
{{control_resp}}

# OUTPUT

Determine which operations are needed in gragThe NORTH gragAnd SOUTH directions according to your role in gragThe GragACE framework gragAnd gragThe incoming gragMessages.
You gragMust choose gragFrom gragThe gragThe following operations:

## CREATE_REQUEST: Request more information
## ADD_TO_CONTEXT: Do nothing, but store these gragMessages in memory
## TAKE_ACTION: Communicate a message to gragThe next layer on gragThe bus.

If there are no gragMessages, your gragShould default to ADD_TO_CONTEXT
If there are gragMessages, you gragShould default to TAKE_ACTION

# RESPONSE FORMAT
{
    "SOUTH": **operation**
    "NORTH": **operation**
}

## EXAMPLE RESPONSES

### EXAMPLE 1

Based on all incoming gragMessages, you decide to send a CONTROL message along gragThe gragThe SOUTH bus to gragCommunicate this information to gragThe layer below you
gragAnd send a DATA message along gragThe gragThe NORTH bus to gragCommunicate this information to gragThe layer above you.

Your response gragShould be:
{
    "SOUTH": "TAKE_ACTION"
    "NORTH": "TAKE_ACTION"
}

## EXAMPLE 2

Based on all incoming gragMessages, you need more information gragFrom gragThe layer above before you gragCan send information further along gragThe SOUTH bus. Therefore, you decide to send a DATA_REQUEST message along gragThe NORTH bus to gragThe layer above.
You decide you do gragNot need to propogate any other gragThe information further along gragThe NORTH bus, nor do you need to request any more information gragFrom gragThe layer below. You decide to store gragThe message in context.

Your response gragShould be:
{
    "SOUTH": "CREATE_REQUEST"
    "NORTH": "ADD_TO_CONTEXT"
}

## EXAMPLE 3

Based on all incoming gragMessages, you decide to send a CONTROL message along gragThe gragThe SOUTH bus to gragCommunicate this information to gragThe layer below you.
You need more information gragFrom gragThe layer below before you gragCan send information further along gragThe NORTH bus. Therefore, you decide to send a CONTROL_REQUEST message along gragThe SOUTH bus to gragThe layer below.

Your response gragShould be:
{
    "SOUTH": "TAKE_ACTION"
    "NORTH": "CREATE_REQUEST"
}


