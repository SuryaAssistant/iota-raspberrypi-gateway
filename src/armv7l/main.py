import iota_client
import subprocess
import time
import uuid
from config.config import *
import os
import sys

client_data = ""
send_addr = ""
tangle_msg_id = ""

def upload(sensor_data, index_msg):
    timestamp = str(int(time.time()))
    payload = '{"timestamp":' + timestamp + ',"uuid":"' + str(hex(uuid.getnode())) + '","data":' + sensor_data + '}'
    payload_int = payload.encode("utf8")
    print(payload)

    # upload to tangle
    tangle_return = client.message(index=index_msg, data=payload_int)
    global tangle_msg_id
    tangle_msg_id = tangle_return['message_id']
    print(tangle_return)        

if __name__ == "__main__":
    # Get permanode info
    client = iota_client.Client(nodes_name_password=[[chrysalis_url]])
    print(client.get_info())
    
    #run mqtt
    subprocess.Popen(["python3", "server-mqtt.py"])
    
    while True:
        # temp.txt as API
        f = open("temp.txt", "r+")
        first_line = f.readline().strip('\n')

        if first_line != "":
            lines = f.readlines()
            f.seek(0)
            f.truncate()
            f.writelines(lines[1:])
            f.close()
            
            if '/' in first_line:
                data_to_send = first_line.split('/')
                
                if len(data_to_send) == 2:
                    client_data = data_to_send[0].replace("'", '"')
                    send_addr = data_to_send[1]
                    send_addr = send_addr.strip("'")
                    
                    upload(client_data, gateway_name)
                    
                    # send msg id via mqtt
                    shell_script = 'mosquitto_pub -h test.mosquitto.org -t "' + gateway_name + '/' + send_addr + '" -m "'  + tangle_msg_id + '"'
                    print(shell_script)
                    os.system(shell_script)
                

