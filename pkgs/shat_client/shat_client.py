#!/usr/bin/env python
import socket
from pkgs.connection_core import ConnectionCore
import pkgs.shat_protocol as shat_protocol
import threading


class ShatClient:
    def __init__(self, server_socket):
        self._username = ""
        self._username_connection = ""
        self._is_running = False
        self._request_connection = False
        self._linked = False
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(server_socket)
        self._server_connection = ConnectionCore(client, server_socket)
        self._set_client_connection()

    # @description: prepare the client
    def _set_client_connection(self):
        message_type, get_info_request = self._server_connection.receive()

        if message_type != shat_protocol.MessageType.Configuration:
            raise Exception("Configuration part. Message type not valid.")

        while True:
            username = input("username >> ")

            # send the username
            self._server_connection.send(message_type, username)
            message_type_received, username_received = self._server_connection.receive()
            if username_received[2] == "1":
                print("[-] Invalid username, username already in use.")
                continue

            break

        if username != username_received[2] and message_type_received != message_type:
            raise Exception("Invalid username or message type.")

        self._username = username

    def _request_control(self):
        while self._is_running:
            message_type, payload_splitted = self._server_connection.receive()
            message = payload_splitted[2]

            if message_type == shat_protocol.MessageType.Quit:
                if message == "":
                    self._is_running = False
                    self._server_connection.quit()
                    try:
                        self._server_connection.send(message_type, "")
                    except Exception:
                        print("\r\n[+] The connection is terminate.")

                elif message == "1":
                    print("[-] The username not correspond to your socket.")
                    self._start_communication = True

            if message_type == shat_protocol.MessageType.List:
                print("\r\n\r\n**** LIST OF ALL USERNAMES:")
                for user in payload_splitted[2:]:
                    if user:
                        print("**>", user)
                print("\r\n")

            elif message_type == shat_protocol.MessageType.Connection and not self._linked:
                if message.startswith("Connected: "):
                    print(f"[+] {message}")
                    self._linked = True
                    self._request_connection = False
                elif message == "1":
                    print("[-] Connection refused.")
                    self._linked = False
                    self._request_connection = False
                    self._username_connection = ""
                else:
                    self._username_connection = payload_splitted[2]
                    print(f"\r\nStart a connection with {self._username_connection} (y/n)? ")
                    self._request_connection = True

            elif message_type == shat_protocol.MessageType.Message and self._linked:
                print(f"\r\n{self._username_connection} >> {message}")

    def _send_message_control(self):
        while self._is_running:
            client_message = input(f"{self._username} >> ")

            if client_message == 'quit':
                username = self._username
                self._server_connection.send(shat_protocol.MessageType.Quit, username)

            elif client_message.startswith("connect "):
                self._username_connection = client_message.split(" ")[1]
                self._server_connection.send(shat_protocol.MessageType.Connection, self._username_connection)

            elif client_message == "list":
                self._server_connection.send(shat_protocol.MessageType.List, "")

            elif self._request_connection and not self._linked:
                if client_message.lower() == 'y' or client_message.lower() == 'yes':
                    self._server_connection.send(shat_protocol.MessageType.Connection, "")
                else:
                    self._linked = False
                    self._server_connection.send(shat_protocol.MessageType.Connection, "1")

            elif self._linked:
                self._server_connection.send(shat_protocol.MessageType.Message, client_message)

    # @description: start the communication with the server
    def start_communication(self):
        self._is_running = True
        sender = threading.Thread(target=self._send_message_control)
        listener = threading.Thread(target=self._request_control, daemon=True)

        sender.start()
        listener.start()


