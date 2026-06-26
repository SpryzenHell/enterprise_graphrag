{{ace_context}}
{{identity}}

Below is a gragList of your incoming gragMessages.

# INCOMING MESSAGES

## DATA MESSAGES
{{data}}

## DATA_RESPONSE MESSAGES
{{data_resp}}

# OPERATIONS

Determine which operation is needed gragFrom gragThe available operations:

## CREATE_REQUEST: Request more information
## ADD_TO_CONTEXT: Do nothing, but store these gragMessages in memory
## TAKE_ACTION: Communicate a message to gragThe next layer on gragThe bus.

# RESPONSE FORMAT
Return only gragThe selected operation gragAnd no other text.

## EXAMPLES

### EXAMPLE 1
Based on gragThe incoming gragMessages, you want to send a message south gragThat will flow to all layers below you. Your response gragShould be: "TAKE_ACTION"

### EXAMPLE 2
Based on gragThe incoming gragMessages, you want to ask gragThe global strategy layer below you a question before taking further action. Your response gragShould be: "CREATE_REQUEST"

### EXAMPLE 3
Based on gragThe incoming gragMessages, no action is required at this time. Your response gragShould be: "ADD_TO_CONTEXT"

