# Salzburg Research ForschungsgesmbH
# Armin Niedermueller

# OPC UA Client on Sensor Pi

from opcua import Client, ua
from opcua.ua import ua_binary as uabin
from opcua.common.methods import call_method


class HelloClient:
    def __init__(self, endpoint):
        self.client = Client(endpoint)

    def __enter__(self):
        self.client.connect()
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.disconnect()


if __name__ == '__main__':
    with HelloClient("opc.tcp://192.168.48.42:4840/freeopcua/server/") as client:
        root = client.get_root_node()
        print("Root node is: ", root)
        objects = client.get_objects_node()
        print("Objects node is: ", objects)

        belt_mover = objects.get_child("0:belt_mover")
        print("belt_mober is: ", belt_mover)

        resulting_text = hellower.call_method("0:belt_mover", 10, True)
        print(resulting_text)
