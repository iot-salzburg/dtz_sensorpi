
# IoT Sensor Pi

The node running this scripts is provides IoT
sensor data like temperature, humidity and energy
consumption. This data is sent via mqtt to a
local broker which integrates mqtt-based applications
into the dtz framework.

## Quickstart

### Installation of the sensor library

In an arbitrary folder:

```bash
git clone https://github.com/adafruit/Adafruit_Python_DHT.git

cd /path/to/Adafruit_Python_DHT

sudo apt-get install build-essential python-dev3

sudo python3 setup.py install
```

In your home folder:
    
```bash
git clone https://github.com/iot-salzburg/dtz_sensorpi.git

cd dtz_sensorpi

sudo pip3 install -r requirements.txt
```


### Starting the script
```bash
python3 measurement.py
```


### Set up Autostart service

```bash
sudo cp configs/sensorpi.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable sensorpi.service
sudo service sensorpi start
```

Check if the service works

```bash
sudo service sensorpi status
```

and check on the node-red mqtt broker [http://il081:1880](http://il081:1880/)
with the settings:

* Server = 192.168.48.81
* Port = 1883
* topic = sensorpi/#


