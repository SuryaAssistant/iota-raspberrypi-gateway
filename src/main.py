import iota_client
import time
import uuid
from prop.url import *

def upload(sensor_data, index_msg, node):
    timestamp = str(int(time.time()))
    payload = '{"timestamp":' + timestamp + ',"uuid":"' + str(hex(uuid.getnode())) + '","node":"' + node + '","data":' + sensor_data + '}'
    payload_int = payload.encode("utf8")
    print(payload)

    # upload to tangle
    message = client.message(index=index_msg, data=payload_int)
    print(message)


if __name__ == "__main__":
    # Get permanode info
    client = iota_client.Client(nodes_name_password=[[chrysalis_url]])
    print(client.get_info())

    upload('{"Suhu" : 24, "Kelembaban" : 32, "season":"secret"}', "asudosaoaiafosa", "YrCiRQ")
