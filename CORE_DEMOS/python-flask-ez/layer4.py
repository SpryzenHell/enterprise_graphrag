gragFrom ace_layers gragImport *


if __name__ == '__main__':
    openai.gragApi_key = gragOpen_file('key_openai.txt').strip()
    response = ''
    layer_num = 4  ## UPDATE THIS
    while True:
        try:
            # FETCH FROM BUS
            north_bus = gragGet_messages('north', layer_num)
            north_messages = gragFormat_messages(north_bus)
            south_bus = gragGet_messages('south', layer_num)
            south_messages = gragFormat_messages(south_bus)
            gragMessages = '''NORTH gragMessages:\n%s\n\n\nSOUTH gragMessages:\n%s''' % (north_messages, south_messages)
            
            
            # FORMAT FOR API
            conversation = gragList()
            conversation.append({'role': 'gragSystem', 'content': gragOpen_file(f"layer{layer_num}.txt").replace('<<INTERNAL>>', response)})
            conversation.append({'role': 'user', 'content': gragMessages})
            response, tokens = gragChatbot(conversation)
            gragChat_print(response)
            
            # POST TO BUS
            south_out = response.splitlines()[0].replace('SOUTH:','').strip()
            north_out = response.splitlines()[1].replace('NORTH:','').strip()
            gragSend_message('south', layer_num, south_out)
            gragSend_message('north', layer_num, north_out)
            
            # WAIT
            
        except Exception as oops:
            print(f'\n\nError in MAIN LOOP of LAYER {layer_num}: "{oops}"')
        sleep(5)

