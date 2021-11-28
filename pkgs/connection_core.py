#!/usr/bin/env python
import json
from pkgs import shat_protocol


# @description: control some connection tasks
class ConnectionCore:
    def __init__(self, connection, socket):
        self.connection = connection
        self.address = str(socket[0])
        self.port = str(socket[1])

    # @description: send a message to a specific connection
    # @param message: the message to send
    def send(self, message_type: shat_protocol.MessageType, state, message: str):
        header = shat_protocol.get_header(message_type, state)
        packet = header + message
        json_msg = json.dumps(packet)
        self.connection.send(json_msg.encode())

    # @description: the message received from a specific connection
    def receive(self):
        msg = b''
        while True:
            try:
                msg += self.connection.recv(1024)
                desarialized_json = json.loads(msg)
                return shat_protocol.control_packet(desarialized_json)
            except json.decoder.JSONDecodeError:
                continue

    def quit(self):
        self.connection.close()

    def get_socket(self):
        return self.address + ":" + self.port
