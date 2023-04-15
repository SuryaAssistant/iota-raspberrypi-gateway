
# Python Program to compute
# MAC address of host
# using UUID module
 
import uuid
 
# printing the value of unique MAC
# address using uuid and getnode() function
print (hex(uuid.getnode()))