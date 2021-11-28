#!/usr/bin/env python
import socket
from pkgs.connection_core import ConnectionCore
import pkgs.shat_client.shat_message as shat_message
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
        message_type, state_type, get_info_request = self._server_connection.receive()

        if message_type != shat_protocol.MessageType.Configuration and state_type != shat_protocol.ConfigurationState.Name:
            raise Exception("Configuration part. Message type not valid.")

        while True:
            username = input("username >> ")

            # send the username
            self._server_connection.send(message_type, state_type, username)
            message_type_received, state_type, username_received = self._server_connection.receive()
            if state_type == shat_protocol.ConfigurationState.WrongUsername:
                print(shat_message.print_negative_message(username_received[3]))
                continue

            break

        if message_type_received != message_type and state_type != shat_protocol.ConfigurationState.NameConfirmed:
            raise Exception("Invalid username or message type.")

        self._username = username

    # @description: reset some value used with the connection
    def _not_connected_status(self):
        self._linked = False
        self._request_connection = False
        self._username_connection = ""

    # @description: an helper to print the username, usually used in the _request_control
    def _print_username(self):
        print(shat_message.print_current_user(self._username), end="", flush=True)

    # @description: control the received message
    def _request_control(self):
        while self._is_running:
            message_type, state_type, payload_splitted = self._server_connection.receive()
            message = payload_splitted[3]

            print("\r\n")

            if message_type == shat_protocol.MessageType.Quit:
                if shat_protocol.QuitState.ConfirmQuit == state_type:
                    self._is_running = False
                    self._server_connection.quit()
                    try:
                        self._server_connection.send(message_type, state_type, "")
                    except Exception:
                        print(shat_message.print_positive_message("The connection is terminate."))

                elif shat_protocol.QuitState.ErrorQuit == state_type:
                    print("[-] The username not correspond to your socket.")
                    self._start_communication = True

            elif message_type == shat_protocol.MessageType.List and shat_protocol.ListState.GetList == state_type:
                print("\r\n**** LIST OF ALL USERNAMES:")
                for user in payload_splitted[3:]:
                    if user:
                        print("**>", user)
                print("\r\n")
                self._print_username()

            elif message_type == shat_protocol.MessageType.Connection and not self._linked:
                if shat_protocol.ConnectionState.Accept == state_type and message.startswith("Connected: "):
                    print(shat_message.print_positive_message(f"{message}"))
                    self._linked = True
                    self._request_connection = False

                elif shat_protocol.ConnectionState.Refuse == state_type:
                    print(shat_message.print_negative_message("Connection refused."))
                    self._not_connected_status()

                elif shat_protocol.ConnectionState.InvalidUsername == state_type:
                    print(shat_message.print_negative_message("Invalid username."))
                    self._not_connected_status()

                elif shat_protocol.ConnectionState.AlreadyConnected == state_type:
                    print(shat_message.print_negative_message("Username already connected."))
                    self._not_connected_status()

                elif shat_protocol.ConnectionState.Request == state_type:
                    self._username_connection = payload_splitted[3]
                    print(shat_message.print_answer_message(f"Start a connection with {self._username_connection} [y/n]? "))
                    self._request_connection = True

                else:
                    print(shat_message.print_answer_message("Wrong state type"))
                    self._not_connected_status()

                self._print_username()

            elif message_type == shat_protocol.MessageType.Connection and self._linked:
                if state_type == shat_protocol.ConnectionState.Disconnect:
                    print(shat_message.print_positive_message(f"Disconnected from {self._username_connection}."))
                    self._not_connected_status()

                self._print_username()

            elif message_type == shat_protocol.MessageType.Message and self._linked:
                connected_user = shat_message.print_connected_user(self._username_connection) + message
                print(connected_user)
                self._print_username()

    def _send_message_control(self):
        while self._is_running:
            client_message = input(shat_message.print_current_user(self._username))

            if client_message == 'quit':
                if not self._linked:
                    username = self._username
                    self._server_connection.send(shat_protocol.MessageType.Quit, shat_protocol.QuitState.Quit, username)
                else:
                    print(shat_message.print_negative_message("Before you quit deactivate the connection `deactivate`"))

            elif client_message.startswith("connect ") and not self._linked and not self._request_connection:
                self._request_connection = True
                self._username_connection = client_message.split(" ")[1]
                self._server_connection.send(shat_protocol.MessageType.Connection, shat_protocol.ConnectionState.Request, self._username_connection)
                print(shat_message.print_positive_message(f'Sent the request, waiting from {self._username_connection} response..'))

            elif client_message == "deactivate" and self._linked:
                self._server_connection.send(shat_protocol.MessageType.Connection, shat_protocol.ConnectionState.Disconnect, "")

            elif client_message == "list":
                self._server_connection.send(shat_protocol.MessageType.List, shat_protocol.ListState.GetList, "")

            elif self._request_connection and not self._linked:
                if client_message.lower() == 'y' or client_message.lower() == 'yes':
                    self._server_connection.send(shat_protocol.MessageType.Connection, shat_protocol.ConnectionState.Accept, "")
                else:
                    self._request_connection = False
                    self._linked = False
                    self._server_connection.send(shat_protocol.MessageType.Connection, shat_protocol.ConnectionState.Refuse, "1")

            elif self._linked and client_message != "":
                self._server_connection.send(shat_protocol.MessageType.Message, shat_protocol.MessageState.Connected, client_message)

    # @description: start the communication with the server
    def start_communication(self):
        self._is_running = True
        sender = threading.Thread(target=self._send_message_control)
        listener = threading.Thread(target=self._request_control, daemon=True)

        sender.start()
        listener.start()


