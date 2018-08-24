import time
import sys
sys.path.insert(0, "..")

from multiprocessing import Process
from opcua import Client


if __name__ == "__main__":

    client = Client("opc.tcp://192.168.48.42:4840/freeopcua/server/")
    # client = Client("opc.tcp://admin@localhost:4840/freeopcua/server/") #connect using a user
    try:
        client.connect()

        # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
        root = client.get_root_node()
        print("Objects node is: ", root)

        # Node objects have methods to read and write node attributes as well as browse or populate address space
        print("Children of root are: ", root.get_children())

        # get a specific node knowing its node id
        #var = client.get_node(ua.NodeId(1002, 2))
        #var = client.get_node("ns=3;i=2002")
        #print(var)
        #var.get_data_value() # get value of node as a DataValue object
        #var.get_value() # get value of node as a python builtin
        #var.set_value(ua.Variant([23], ua.VariantType.Int64)) #set node value using explicit data type
        #var.set_value(3.9) # set node value using implicit data type

        # Now getting a variable node using its browse path
        server_time = root.get_child(["0:Objects", "2:Object1", "2:Time"])
        object1 = root.get_child(["0:Objects", "2:Object1"])
        mover = root.get_child(["0:Objects", "2:Object1", "2:MoveBelt"])
        #object1 = root.get_child(["0:Objects", "2:MyObject"])
        object1.call_method("2:MoveBelt", True)
        print("first call")

        print("time is: ", server_time)
        print("object1 is: ", object1)

        time.sleep(14)

        object1.call_method("2:MoveBelt", False)
        print("second call")
    finally:
        client.disconnect()
