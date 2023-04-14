import iota_client
import time
from prop.url import *

def upload(sensor_data, sp_msg, index_msg):
    timestamp = str(int(time.time()))
    payload = '{"timestamp":' + timestamp + ',"special_message":"' + sp_msg +  '","data":' + sensor_data + '}'
    payload_int = payload.encode("utf8")
    print(payload)

    # upload to tangle
    message = client.message(index=index_msg, data=payload_int)
    print(message)

# Get permanode info
client = iota_client.Client(nodes_name_password=[[chrysalis_url]])
print(client.get_info())

upload('{"Suhu" : 32, "Kelembaban" : 60}', "YrCiRQ", "asudosaoaiafosa")
