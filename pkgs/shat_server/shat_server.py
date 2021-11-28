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
        self._client_connection.send(shat_protocol.MessageType.Configuration, shat_protocol.ConfigurationState.NameConfirmed, self._client_connection.username)

    # @description: control if the username is valid
    def _control_username(self):
        configuration_state = shat_protocol.ConfigurationState.Name
        message = ""

        while True:
            # send an info request
            self._client_connection.send(shat_protocol.MessageType.Configuration, configuration_state, message)

            # read the received info
            message_type, state_type, packet_list = self._client_connection.receive()
            if message_type != shat_protocol.MessageType.Configuration and state_type == shat_protocol.ConfigurationState.Name:
                raise Exception("Invalid type, must be a Configuration type state Name.")

            username = packet_list[3]
            if username == "":
                configuration_state = shat_protocol.ConfigurationState.WrongUsername
                message = "Empty username"
                continue
            elif " " in username:
                configuration_state = shat_protocol.ConfigurationState.WrongUsername
                message = "The username can't have empty space"
                continue
            elif self._exist_username(username):
                configuration_state = shat_protocol.ConfigurationState.WrongUsername
                message = "The username already exist"
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
            message_type, state_type, packet_list = self._client_connection.receive()
            message = packet_list[3]

            if message_type == shat_protocol.MessageType.Quit and state_type == shat_protocol.QuitState.Quit:
                username = message
                socket_client = self._client_connection.get_socket()

                if _connections.get(socket_client)["username"] == username:
                    del _connections[socket_client]
                    self._client_connection.send(message_type, shat_protocol.QuitState.ConfirmQuit, "")
                    print(f'[+] Deleted {username}.')
                    break
                else:
                    self._client_connection.send(message_type, shat_protocol.QuitState.ErrorQuit, "Wrong username")
                    print(f"[-] Wrong username. Username requested to delete is {username}.")

            elif message_type == shat_protocol.MessageType.List and state_type == shat_protocol.ListState.GetList:
                message = ""
                for user in _connections.values():
                    message += user["username"] + "\r\n"

                self._client_connection.send(message_type, state_type, message)

            elif message_type == shat_protocol.MessageType.Connection:
                if state_type == shat_protocol.ConnectionState.Disconnect:
                    self._client_connection.send(message_type, shat_protocol.ConnectionState.Disconnect, "")
                    self._client_connection.connected.send(message_type, shat_protocol.ConnectionState.Disconnect, "")
                    self._client_connection.connected.connected = None
                    self._client_connection.connected = None
                elif state_type == shat_protocol.ConnectionState.Request:
                    username = message

                    if username != self._client_connection.username:
                        connection = self._exist_username(username)

                        if connection and not connection.connected:
                            connection.send(shat_protocol.MessageType.Connection, shat_protocol.ConnectionState.Request, self._client_connection.username)

                            message_type, state_type, packet_list = connection.receive()
                            if state_type == shat_protocol.ConnectionState.Accept:
                                connection.connected = self._client_connection
                                self._client_connection.connected = connection
                                self._client_connection.send(shat_protocol.MessageType.Connection, shat_protocol.ConnectionState.Accept, f"Connected: {connection.username}")
                                connection.send(shat_protocol.MessageType.Connection, shat_protocol.ConnectionState.Accept, f"Connected: {self._client_connection.username}")

                            else:
                                self._client_connection.send(shat_protocol.MessageType.Connection, shat_protocol.ConnectionState.Refuse, "")
                                connection.connected = None
                                self._client_connection.connected = None
                        elif connection and connection.connected:
                            self._client_connection.send(message_type, shat_protocol.ConnectionState.AlreadyConnected, f"Already connected to {connection.connected.username}")
                        else:
                            self._client_connection.send(message_type, shat_protocol.ConnectionState.InvalidUsername, "Connection not found")
                    else:
                        self._client_connection.send(message_type, shat_protocol.ConnectionState.InvalidUsername, "Username not found")

            elif message_type == shat_protocol.MessageType.Message and state_type == shat_protocol.MessageState.Connected and self._client_connection.connected:
                self._client_connection.connected.send(message_type, state_type, message)

        self._client_connection.quit()

    # @description: start the communication between the client and server
    def activate_communication(self):
        communication = threading.Thread(target=self._communication_control)
        communication.start()



