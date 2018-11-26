#      _____         __        __                               ____                                        __
#     / ___/ ____ _ / /____   / /_   __  __ _____ ____ _       / __ \ ___   _____ ___   ____ _ _____ _____ / /_
#     \__ \ / __ `// //_  /  / __ \ / / / // ___// __ `/      / /_/ // _ \ / ___// _ \ / __ `// ___// ___// __ \
#    ___/ // /_/ // /  / /_ / /_/ // /_/ // /   / /_/ /      / _, _//  __/(__  )/  __// /_/ // /   / /__ / / / /
#   /____/ \__,_//_/  /___//_.___/ \__,_//_/    \__, /      /_/ |_| \___//____/ \___/ \__,_//_/    \___//_/ /_/
#                                              /____/
# Salzburg Research ForschungsgesmbH
# Armin Niedermueller

# OPC UA Server on SensorPi
# The purpose of this OPCUA server is to simulate the FH Salzburg's OPC UA Server

from opcua import ua, uamethod, Server
import datetime
import logging
import time
import sys




if __name__ == "__main__":

    logging.basicConfig(filename='/home/pi/dtz_sensorpi/opc_server_pixtend.log', filemode='w', level=logging.INFO)
    # setup our server
    server = Server()
    url = "opc.tcp://0.0.0.0:4840/freeopcua/server"
    server.set_endpoint(url)

    # setup our own namespace
    uri = "https://github.com/iot-salzburg/dtz_sensorpi"
    idx = server.register_namespace(uri)


    # get Objects node, this is where we should put our nodes
    objects = server.get_objects_node()

    # Add a parameter object to the address space
    plc_object = objects.add_object(idx, "PLC")

    # Parameters - Addresspsace, Name, Initial Value
    server_time = plc_object.add_variable(idx, "ServerTime", 0)

    desired_storage = plc_object.add_variable(idx, "ShelfNumber", 0)
    new_val_available = plc_object.add_variable(idx, "NewValueAvailable", False)
    task_running = plc_object.add_variable(idx, "TaskRunning", False)


    # Set parameters writable by clients
    server_time.set_writable()
    desired_storage.set_writable()
    new_val_available.set_writable()
    task_running.set_writable()


    # Start the server
    server.start()
    logging.info("OPCUA - FH Emulation on SensorPi - Server started at {}".format(url))

    try:
        # Assign random values to the parameters

        while True:
            TIME = datetime.datetime.utcnow()  # current time
            with open ("./shelf", "r") as f:
                shelf_state = f.read()
                desired_storage.set_value(int(shelf_state))
            with open ("./newvalavailable", "r") as f:
                nva = f.read()
                if "true" in nva:
                    new_val_available.set_value(True)
                else:
                    new_val_available.set_value(False)

            # set the random values inside the node
            logging.info("NewValueAvailable: " + str(new_val_available.get_value()) + "\nRegalnummer: " + str(desired_storage.get_value()) + "\nServer-Time: " + str(server_time.get_value()))
            server_time.set_value(TIME)

            # sleep 1 second
            time.sleep(1)
    except KeyboardInterrupt:
            logging.info("\nCtrl-C pressed. OPCUA - Pixtend - Server stopped at {}".format(url))
    finally:
        #close connection, remove subcsriptions, etc
        server.stop()
        conbelt = None
        sys.exit(0)

