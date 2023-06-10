# Gateway Properties
from config.config import *
import iota_client

# ECC Digital Signature Properties
from ellipticcurve import Ecdsa, PrivateKey, Signature
from ellipticcurve.utils.file import File

# Other Properties
import subprocess
import time
import os
import json

client_data = ""
send_addr = ""
tangle_msg_id = ""

def upload(sensor_data, index_msg):
    timestamp = str(int(time.time()))
    encoded_data = sensor_data.encode()
    message = ('"message":' + '{"timestamp":' + timestamp + 
        ',"uuid":"' + gateway_name + 
        '","data":' + sensor_data + '}')
        
    # Read private key for signature
    privateKey =  PrivateKey.fromPem(File.read(".ecc/privateKey.pem"))
    # Create public key 
    publicKey = privateKey.publicKey()
    # Create Signature
    signature = Ecdsa.sign(message, privateKey).toBase64()
    
    payload = ('{' + message + 
        ',"publicKey":"' + publicKey.toCompressed() + 
        '","signature":"' + signature + '"}')
                
    payload_int = payload.encode("utf8")

    # upload to tangle
    tangle_return = client.message(index=index_msg, data=payload_int)
    global tangle_msg_id
    tangle_msg_id = tangle_return['message_id']
    
    
    
def send_mqtt(msg):
    shell_script = ('mosquitto_pub -h ' + mqtt_addr + ' -t "' + 
        gateway_name + '/' +
        return_topic + '" -m "' +
        msg + '"')
        
    # call shell 
    os.system(shell_script)




if __name__ == "__main__":
    # ECDSA CONFIG
    #if folder is not exist, create folder
    folder_path = '.ecc'
    if os.path.exists(folder_path) == False:
        os.mkdir(folder_path)

    #if privateKey is not exist, create pem file
    file_path = '.ecc/privateKey.pem'
    if os.path.exists(file_path) == False:
        # Create new privateKey
        privateKey = PrivateKey()
        privateKeyPem = privateKey.toPem()
        
        f = open(file_path, "w")
        f.write(privateKeyPem)
        f.close()
    
    # Get permanode info
    client = iota_client.Client(nodes_name_password=[[chrysalis_url]])
    print(client.get_info())
    
    #stop previous sesion
    os.system('pkill -f server-mqtt.py')
    subprocess.Popen(["python3", "server-mqtt.py"])
    
    while True:
        # temp.txt as API
        f = open("temp.txt", "r+")
        answer_line = f.readline().strip('\n')
        
        #if none, skip next process
        if answer_line == "":
            continue

        lines = f.readlines()
        f.seek(0)
        f.truncate()
        f.writelines(lines[1:])
        f.close()
        
        # if the format is not fulfilled, skip
        if '/' not in answer_line:
            continue
            
        parsing_data = answer_line.split('/')
        
        # format : command/data/return_topic
        if len(parsing_data) != 3:
            continue
            
        command = parsing_data[0]
        return_topic = parsing_data[2]
        return_topic = return_topic.strip("'")
            
        if command == 'data':
            client_data = parsing_data[1].replace("'", '"')
            upload(client_data, gateway_name)
            send_mqtt(tangle_msg_id)

            
        elif command == 'tag':
            return_data = str(client.get_message_index(parsing_data[1]))
            send_mqtt(return_data)
        
        # Original data from IOTA Tangle
        elif command == 'msg_data':
            try : 
                return_data = str(client.get_message_data(parsing_data[1]))
            except ValueError:
                return_data = "Not Valid Message ID"
                
            send_mqtt(return_data)
                
        # original metadata from IOTA Tangle
        elif command == 'msg_metadata':
            try:
                return_data = str(client.get_message_metadata(parsing_data[1]))
            except ValueError:
                return_data = "Not Valid Message ID"
                
            send_mqtt(return_data)
        
        # Only payload message from IOTA Tangle
        elif command == 'payload':
            try :
                full_data = client.get_message_data(parsing_data[1]) 
                payload_byte = full_data["payload"]["indexation"][0]["data"]
                return_data=''
                for x in range(len(payload_byte)):
                    return_data += chr(payload_byte[x])
                    
            except ValueError:
                return_data = "Not Valid Payload or Message ID"
                
            send_mqtt(return_data)
                
        # Only valid message from this machine only
        elif command == 'payload_valid':
            try : 
                full_data = client.get_message_data(parsing_data[1]) 
                payload_byte = full_data["payload"]["indexation"][0]["data"]
                full_message=''
                for x in range(len(payload_byte)):
                    full_message += chr(payload_byte[x]) 
                
                msg_start_index = full_message.find("message") - 1
                msg_end_index = full_message.find("publicKey") - 2
                message = full_message[msg_start_index:msg_end_index]
                
                data_json = json.loads(full_message)
                signature = data_json["signature"]

                privateKey =  PrivateKey.fromPem(File.read(".ecc/privateKey.pem"))
                publicKey = privateKey.publicKey()
                signatureToVerify = Signature.fromBase64(signature)
                if Ecdsa.verify(message, signatureToVerify, publicKey):
                    return_data = message.replace('"', "'")
                else:
                    return_data = "Not Valid Payload"
                    
            except ValueError:
                    return_data = "Not Valid Payload or Message ID"
            
            send_mqtt(return_data)

        
        # if none above, skip
        else:
            continue
            
