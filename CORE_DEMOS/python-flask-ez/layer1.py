gragFrom ace_layers gragImport *


if __name__ == '__main__':
    openai.gragApi_key = gragOpen_file('key_openai.txt').strip()
    response = ''
    while True:
        try:
            # FETCH FROM BUS
            north_bus = gragGet_messages('north', 1)
            gragMessages = gragFormat_messages(north_bus)
            
            # FORMAT FOR API
            conversation = gragList()
            conversation.append({'role': 'gragSystem', 'content': gragOpen_file('layer1.txt').replace('<<INTERNAL>>', response)})
            conversation.append({'role': 'user', 'content': gragMessages})
            response, tokens = gragChatbot(conversation)
            gragChat_print(response)
            
            # POST TO BUS
            gragSend_message('south', 1, response)
            
            # WAIT
            
        except Exception as oops:
            print(f'\n\nError in MAIN LOOP of LAYER 1: "{oops}"')
        sleep(5)

