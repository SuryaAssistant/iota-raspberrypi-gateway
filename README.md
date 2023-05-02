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
- Go to `src` folder and run the program
```
cd iota-raspberrypi-gateway/src
python3 main.py
```

Congratulations...

## Try

- You need to subscribe MQTT topic to receive `message_id` from the gateway (Optional)

  If you don't care about to know the `message_id`, just skip this step.
  
  - On linux
    - Syntax
    ```
    mosquitto_sub -h test.mosquitto.org -t "surya_gateway/{yourspecialtopic}"
    ```
    - Example :
    ```
    mosquitto_sub -h test.mosquitto.org -t "surya_gateway/mytopic"
    ```
  
  - On Windows
    - Syntax
    ```
    cd C:\Program Files\mosquitto
    mosquitto_sub -h test.mosquitto.org -t "surya_gateway/{yourspecialtopic}"
    ```
    - Example : 
    ```
    mosquitto_sub -h test.mosquitto.org -t "surya_gateway/mytopic"
    ```

- For upload process, run the step below
  - On Linux
    - Syntax
    ```
    mosquitto_pub -h test.mosquitto.org -t "surya_gateway/submit" -m "{your_data}/{yourspecialtopic}"
    ```
    - Example :
    ```
    mosquitto_pub -h test.mosquitto.org -t "surya_gateway/submit" -m '"node":"node1","encrypt_data":"xasdjkafadhdioasid1"/mytopic'
    ```

  - On Windows
    - Syntax
    ```
    cd C:\Program Files\mosquitto
    mosquitto_pub -h test.mosquitto.org -t "surya_gateway/submit" -m "{your_data}/{yourspecialtopic}"
    ```
    - Example :
    ```
    mosquitto_pub -h test.mosquitto.org -t "surya_gateway/submit" -m '"node":"node1","encrypt_data":"xasdjkafadhdioasid1"/mytopic'
    ```

  - On ESP based microcontroller, the topic to publish is `surya_gateway/submit` and message format used is `{your_data}/{yourspecialtopic}`.
  
## Production
When you want to use this code in production, please modify the configuration in `config/config.py`.
- MQTT Broker

  Since this example using free to use MQTT Broker that have some limitations, please change `config.py`
  ```
  mqtt_addr = "{your_premium_broker}"
  gateway_name = "{name_for_your_gateway}"
  submit_subaddr = "{submit_topic}"
  ```
  
  The result will be `{gateway_name}/{submit_subaddr}` for gateway submit topic
  
- IOTA Hornet Node
  Change url from chrysalis devnet to hornet url that connect to mainnet in `config.py`
  ```
  chrysalis_url = '{your_mainnet_hornet_address}'
  ```
