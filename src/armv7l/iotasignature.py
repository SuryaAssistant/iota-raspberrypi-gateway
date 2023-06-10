# IOTA Properties
from config.config import *
import iota_client
import json

from ellipticcurve import Ecdsa, PrivateKey, Signature
from ellipticcurve.utils.file import File

client = iota_client.Client(nodes_name_password=[['https://api.lb-0.h.chrysalis-devnet.iota.cafe']])

data = client.get_message_data("429e3820a905b9cef1467c2bab1dc9172829cbd655b7dc5a2640329fee348c6a") 
payload_data = data["payload"]["indexation"][0]["data"]

data_utf = ""

for x in range(len(payload_data)):
	data_utf += chr(payload_data[x])

msg_start_index = data_utf.find("message") - 1
msg_end_index = data_utf.find("publicKey") - 2

message = data_utf[msg_start_index:msg_end_index]

data_json = json.loads(data_utf)
signature = data_json["signature"]

privateKey =  PrivateKey.fromPem(File.read(".ecc/privateKey.pem"))
publicKey = privateKey.publicKey()


# Read signature base64
signatureVerify = Signature.fromBase64(signature)

print(Ecdsa.verify(message, signatureVerify, publicKey))
