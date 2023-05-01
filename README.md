<!-- Title -->
<span align = "center">

# IOTA Raspberry Pi Gateway

Simplify the way to upload to IOTA Tangle via MQTT. 

</span>
<!-- End of Title -->

<br>
<span align = "center">
   
![Logo](https://github.com/SuryaAssistant/iota-raspberrypi-gateway/blob/main/new_iota.png)

</span>
<br>


This method used to simplify other IoT node such as ESP8266 and ESP32 or the others. Just send to this gateway via MQTT and... voila... it is on Tangle.
As default, this code work on `Chrysalis Devnet`. If you want to use in production, please install hornet or collaborate with someone who has a hornet API to Chrysalis Mainnet.

## Prequerities
- Python 3.x
- pip

## Install Required Dependency

- Install Mosquitto
```
sudo apt-get install mosquitto
sudo apt-get install mosquitto-clients
```
- Install Paho MQTT
```
pip install paho-mqtt
```

Since newer mosquitto didn't support anonymous message, you need to allow it manually.
```
sudo nano /etc/mosquitto/mosquitto.conf
```
and add this lines
```
listener 1883
allow_anonymous true
```

## Clone Repository
- Open terminal and 
```
git clone https://github.com/SuryaAssistant/iota-raspberrypi-gateway
```
- Move to `src` folder and run the program
```
cd iota-raspberrypi-gateway/src
python3 main.py
```

Congratulations...

## Try

- You need to subscribe MQTT topic to receive `message_id` from the gateway (Optional)

  If you don't care about to know the `message_id`, just skip this step.
  
  - On linux
  ```
  mosquitto -h test.mosquitto.org -t "surya_gateway/{yourspecialtopic}"
  ```
  
  - On Windows
  ```
  cd C:\Program Files\mosquitto
  mosquitto -h test.mosquitto.org -t "surya_gateway/{yourspecialtopic}"
  ```
  
- For upload process, run the step below
  - On Linux
  ```
  mosquitto -h test.mosquitto.org -t "surya_gateway/submit" -m "{your_data}/{yourspecialtopic}"
  ```

  - On Windows
  ```
  cd C:\Program Files\mosquitto
  mosquitto -h test.mosquitto.org -t "surya_gateway/submit" -m "{your_data}/{yourspecialtopic}"
  ```
  
  - On ESP based microcontroller, the topic to publish is `surya_gateway/submit` and message format used is `{your_data}/{yourspecialtopic}`.
  
## Production
When you want to use this code in production, please modify the configuration below.
- MQTT Broker

  Since this example using free to use MQTT Broker that have some limitations, please change `src/server-mqtt.py`
  ```
  MQTT_SERVER = "{your_premium_broker}"
  MQTT_PATH = "{your_msg_submission_topic}"
  ```
  
  Also, change the message index for IOTA Tangle and topic to receive message_id in `src/main.py`
  ```
  upload(client_data, "{your_index}", "{your_node_name}")
  ```
  ```
  shell_script = 'mosquitto_pub -h test.mosquitto.org -t "{your_new_topic}/' + send_addr + '" -m "'  + tangle_msg_id + '"'
  ```
- IOTA Hornet Node
  Change url from chrysalis devnet to hornet url that connect to mainnet in `src/prop/url.py`
  ```
  chrysalis_url = '{your_mainnet_hornet_address}'
  ```
