#!/usr/bin/env python
import socket
from pkgs.shat_server.connection_client import ConnectionClient
import pkgs.shat_protocol as shat_protocol
import threading


_connections = {}


class ShatServer:
    def __init__(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("", 6969))
        server.listen(0)
        self._get_client_connection(server)

    # @description: get the client configuration
    def _get_client_connection(self, server):
        print('[+] Waiting for incoming connections.')
        connection, address = server.accept()
        self._client_connection = ConnectionClient(connection, address)
        print(f'[+] Got a connection from {self._client_connection.address}.')

        username = self._control_username()

        self._client_connection.username = username
        _connections[self._client_connection.get_socket()] = {"username": username, "connection": self._client_connection}
        print(f"[+] Added new username {self._client_connection.username}, the ip address is {self._client_connection.address}")

        # send back the approved username
        self._client_connection.send(shat_protocol.MessageType.Configuration, self._client_connection.username)

    # @description: control if the username is valid
    def _control_username(self):
        error_code = ""

        while True:
            # send an info request
            self._client_connection.send(shat_protocol.MessageType.Configuration, error_code)
            error_code = ""

            # read the received info
            message_type, packet_list = self._client_connection.receive()
            if message_type != shat_protocol.MessageType.Configuration:
                raise Exception("Invalid type, must be a Configuration type.")

            username = packet_list[2]
            if self._exist_username(username):
                error_code = "1"
                continue
            return username

    # @description: control if a username exists in the list
    # @param username: the username to find
    def _exist_username(self, username):
        for connection in _connections.values():
            if username == connection["username"]:
                return connection["connection"]

        return None

    # @description: the main communication between client and server
    def _communication_control(self):
        while True:
            message_type, packet_list = self._client_connection.receive()
            message = packet_list[2]

            if message_type == shat_protocol.MessageType.Quit:
                username = message
                socket_client = self._client_connection.get_socket()

                if _connections.get(socket_client)["username"] == username:
                    del _connections[socket_client]
                    self._client_connection.send(message_type, "")
                    print(f'[+] Deleted {username}.')
                    break
                else:
                    self._client_connection.send(message_type, "1")
                    print(f"[-] Wrong username. Username requested to delete is {username}.")

            elif message_type == shat_protocol.MessageType.List and message == "":
                message = ""
                for user in _connections.values():
                    message += user["username"] + "\r\n"

                self._client_connection.send(message_type, message)

            elif message_type == shat_protocol.MessageType.Connection:
                username = message
                connection = self._exist_username(username)

                if connection:
                    connection.send(shat_protocol.MessageType.Connection, self._client_connection.username)

                    message_type, packet_list = connection.receive()
                    if packet_list[2] == "":
                        connection.connected = self._client_connection
                        self._client_connection.connected = connection
                        self._client_connection.send(shat_protocol.MessageType.Connection, f"Connected: {connection.username}")
                        connection.send(shat_protocol.MessageType.Connection, f"Connected: {self._client_connection.username}")

                    else:
                        self._client_connection.send(shat_protocol.MessageType.Connection, "1")
                        connection.connected = None
                        self._client_connection.connected = None

            elif message_type == shat_protocol.MessageType.Message:
                self._client_connection.connected.send(message_type, message)

        self._client_connection.quit()

    # @description: start the communication between the client and server
    def activate_communication(self):
        communication = threading.Thread(target=self._communication_control)
        communication.start()



