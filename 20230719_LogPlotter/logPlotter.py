import json

with open('log.json') as json_file:
    fields = json.load(json_file)

   
log = []
for i in range(len(fields['fields'])):
    val = fields['fields'][i]['message']
    time = fields['fields'][i]['time']
    if 'pll' in val:
        log.append(time)
        log.append(val)
    # if 'freq' in val:
    #     log.append(time)
    #     log.append(val)



log.reverse()



# with open('C:\\Scratch\\logOut.txt', 'w') as outfile:
#   outfile.write('\n'.join(str(i) for i in log))
    