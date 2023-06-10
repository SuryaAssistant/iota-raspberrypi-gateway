from ellipticcurve import Ecdsa, PrivateKey, Signature
from ellipticcurve.utils.file import File
import os

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


#read private key and try to signature
privateKey =  PrivateKey.fromPem(File.read(".ecc/privateKey.pem"))
publicKey = privateKey.publicKey()
print(publicKey.toPem())

message = "My test message"

# Generate Signature
signature = Ecdsa.sign(message, privateKey)
signature_der = signature.toDer().encode('base64')
print("der format")
print(signature_der)
print("der utf8")
print(signature_der.encode('utf-8'))
signature_base64 = signature.toBase64()
print("base64 format")
print(signature_base64)

# Read signature base64
signatureVerify = Signature.fromBase64(signature_base64)

print(Ecdsa.verify(message, signatureVerify, publicKey))

'''
# Generate new Keys
privateKey = PrivateKey()
privateKey_vars = vars(privateKey)
print(privateKey.toPem())
#write file
print(File.read("privateKey.pem"))
print("original private key : ")
print(privateKey_vars)

publicKey = privateKey.publicKey()
publicKey_vars = vars(publicKey)
publicKey_point = vars(publicKey_vars["point"])
publicKey_curve = vars(publicKey_vars["curve"])
print("public key point : ")
print(publicKey_point)
print("public key curve : ")
print(publicKey_curve)
print(publicKey.toPem())
print("public from pem")
publicKeynew = PublicKey.fromPem(publicKeyPem)
print(publicKeynew)
'''
'''

'''
