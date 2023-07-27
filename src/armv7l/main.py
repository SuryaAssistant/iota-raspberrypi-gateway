#=======================================================================
# IOTA Raspberry Pi Gateway
#
# This project aims to give an easy to use command for other machine to 
# interact with IOTA Tangle. 
#
# This program can be used to give signature to the data. This method is
# helpful to differentiate message in the same tag index by using
# ECDSA signature.
#
# More information : 
# https://github.com/SuryaAssistant/iota-raspberrypi-gateway
#
# Apache-2.0 License
#=======================================================================

# Gateway Properties
from config.config import *
import iota_client

# ECC Digital Signature Properties
from ellipticcurve import Ecdsa, PrivateKey, Signature
from ellipticcurve.utils.file import File

# Other Properties
import subprocess
import json
import time
import os

client_data = ""
send_addr = ""
tangle_msg_id = ""

#=======================================================================
# Function to Upload Data to IOTA Tangle
# Parameter:
# - input_data : Series of data to be uploaded
# - index_msg  : tag index in IOTA Tangle. For easy search by tag index
#=======================================================================
def upload(sensor_data, index_msg):
    timestamp = str(int(time.time()))
    encoded_data = sensor_data.encode()
    message = ('"message":' + '{"timestamp":' + timestamp + 
        ',"data":' + sensor_data + '}')
        
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
    
#=======================================================================
# Function to relay data from IOTA Tangle to Subscriber via MQTT
# Parameter:
# - msg : message from IOTA Tangle
#=======================================================================
def send_mqtt(msg, send_topic):
    shell_script = ('mosquitto_pub -h ' + mqtt_addr + ' -t "' + 
        gateway_name + '/' +
        send_topic + '" -m "' +
        msg + '"')
    
    # see what send
    print('OUT ==> ' + msg)
    # call shell 
    os.system(shell_script)

#=======================================================================
# Function to create and save ECDSA private key
# Parameter: None
#=======================================================================
def ECDSA_begin():
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

#=======================================================================
# Function to act based on input command in API
# Parameter:
# - command : command to do
# - parameter_value : value to input in command
# - return_topic : topic used to send MQTT
#=======================================================================
def do_command(command, parameter_value, return_topic, set_tag=gateway_name):
    # get data section of a message
    if command == 'data':
        try :
            parameter_value = parameter_value.replace("'", '"')
            upload(parameter_value, gateway_name)
            send_mqtt(tangle_msg_id, return_topic)
        except ValueError :
            send_mqtt("Error to upload to Tangle", return_topic)
            
    # Upload data with specified tag index
    elif command == 'data_special':
        try :
            print("Upload to Tangle")
            parameter_value = parameter_value.replace("'", '"')
            upload(parameter_value, set_tag)
            send_mqtt(tangle_msg_id, return_topic)
        except ValueError :
            send_mqtt("Error to upload to Tangle", return_topic)
            
    # get list of message_id based on indexation name
    elif command == 'tag':
        try :
            return_data = str(client.get_message_index(parameter_value))
        except ValueError :
            return_data = "Tag not found"
        send_mqtt(return_data, return_topic)

    # Original data from IOTA Tangle
    elif command == 'msg_data':
        try : 
            return_data = str(client.get_message_data(parameter_value))
        except ValueError:
            return_data = "Message ID not found"
        send_mqtt(return_data, return_topic)
            
    # original metadata from IOTA Tangle
    elif command == 'msg_metadata':
        try:
            return_data = str(client.get_message_metadata(parameter_value))
        except ValueError:
            return_data = "Message ID not found"
        send_mqtt(return_data, return_topic)
        
    # get list of message in tag index
    elif command == 'tag_msg':
        try :
            msg_id_list= client.get_message_index(parameter_value)
            msg_count = len(msg_id_list)
            return_data = "["
            
            for i in range(msg_count):
                # get the payload section
                full_data = client.get_message_data(msg_id_list[i]) 
                payload_byte = full_data["payload"]["indexation"][0]["data"]
                msg=''
                for x in range(len(payload_byte)):
                    msg += chr(payload_byte[x])
                return_data += "[" + msg + "]"
                if i < msg_count-1:
                    return_data += ","
            
            return_data += "]"
            return_data = return_data.replace('"', "'")
        except ValueError :
            return_data = "Tag not found"
            
            
        send_mqtt(return_data, return_topic)
        
    # Only payload message from IOTA Tangle
    elif command == 'payload':
        try :
            # get the payload section
            full_data = client.get_message_data(parameter_value) 
            payload_byte = full_data["payload"]["indexation"][0]["data"]
            return_data=''
            for x in range(len(payload_byte)):
                return_data += chr(payload_byte[x])
        except ValueError:
            return_data = "Not Valid Payload or Message ID"
        return_data = return_data.replace('"', "'")
        send_mqtt(return_data, return_topic)
            
    # Only valid message from this gateway only
    elif command == 'payload_valid':
        try : 
            full_data = client.get_message_data(parameter_value) 
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
                return_data = "Not a Payload from This Gateway"
        except ValueError:
                return_data = "Not a Valid Payload or Message ID"
        send_mqtt(return_data, return_topic)
        
#=======================================================================
# Main program
# In first run, it will:
# - Create Random Private and Public Key
# 
# Next, it will act based on input command from MQTT input.
# Command List :
# - data : upload data to IOTA Tangle. (input: JSON data)
# - tag : get list of msg_id from input index. (input : indexation name)
# - msg_data : get full data of msg. (input : message id)
# - msg_metada : get metadata of msg. (input : message id)
# - payload : get payload of message. (input : message id)
# - payload_valid : get payload of message that uploaded via 
#           this gateway. (input: message_id)
#=======================================================================
if __name__ == "__main__":
    # Configure ECDSA
    ECDSA_begin()
    
    # Test connection with permanode
    client = iota_client.Client(nodes_name_password=[[chrysalis_url]])
    print(client.get_info())
    
    # Stop previous sesion
    # It is necessary to prevent duplicate input message in temp.txt
    os.system('pkill -f server-mqtt.py')
    subprocess.Popen(["python3", "server-mqtt.py"])
    
    while True:
        # Open temp.txt API
        f = open("temp.txt", "r+")
        answer_line = f.readline().strip('\n')
        
        # if none, skip to restart
        if answer_line == "":
            continue

        # if there is message to act,
        # read the first row and delete it
        lines = f.readlines()
        f.seek(0)
        f.truncate()
        f.writelines(lines[1:])
        f.close()
        
        # if the message command format is not fulfilled, skip
        # format must be "command/data_parameter/mqtt_return_topic"
        # if the format is correct, parse message command as 3 parameter
        if '/' not in answer_line:
            continue
        
        parsing_data = answer_line.split('/')
        
        if len(parsing_data) != 3 and len(parsing_data) != 4:
            continue
        
        # Three command style
        if len(parsing_data) == 3:
            input_command = parsing_data[0]
            input_parameter_value = parsing_data[1]
            topic = parsing_data[2].strip("'")
            specified_tag = gateway_name

        # Four command style
        if len(parsing_data) == 4:
            input_command = parsing_data[0]
            specified_tag = parsing_data[1]
            input_parameter_value = parsing_data[2]
            topic = parsing_data[3].strip("'")
                    
        # Do message based on it command function
        do_command(input_command, input_parameter_value, topic, specified_tag)
