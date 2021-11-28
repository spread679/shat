#!/usr/bin/env python
import enum


# @description: the different communication
class MessageType(enum.Enum):
    Configuration = 1
    Quit = 2
    Message = 3
    Connection = 4
    List = 5


class ConfigurationState(enum.Enum):
    Start = "1-00"
    Name = "1-01"
    NameConfirmed = "1-02"
    WrongUsername = "1-03"


class QuitState(enum.Enum):
    Quit = "2-00"
    ConfirmQuit = "2-01"
    ErrorQuit = "2-02"


class MessageState(enum.Enum):
    NoConnected = "3-00"
    Connected = "3-01"


class ConnectionState(enum.Enum):
    Request = "4-00"
    Accept = "4-01"
    Refuse = "4-02"
    InvalidUsername = "4-03"
    AlreadyConnected = "4-04"
    Disconnect = "4-05"


class ListState(enum.Enum):
    GetList = "5-00"


# @description: prepare the header to send
# @param message_type: the message type to prepare
def _get_shat_header(message_type: MessageType, state_type: enum.Enum):
    header = 'SHAT v1.0.0\r\n'
    header += 'MessageType: ' + str(message_type.value) + '\r\n'
    header += "State: " + state_type.value + "\r\n"
    return header


def _control_state(message_type: MessageType, state):
    if message_type == MessageType.Configuration:
        return ConfigurationState(state)
    elif message_type == MessageType.Quit:
        return QuitState(state)
    elif message_type == MessageType.Message:
        return MessageState(state)
    elif message_type == MessageType.Connection:
        return ConnectionState(state)
    elif message_type == MessageType.List:
        return ListState(state)
    else:
        raise TypeError("Invalid state type")


def get_header(message_type: MessageType, state: enum.Enum):
    state_type = _control_state(message_type, state)
    return _get_shat_header(message_type, state_type)


def control_packet(message: str):
    split_message = message.split('\r\n')

    message_type_line = split_message[1]
    state_type_line = split_message[2]

    message_type = MessageType(int(message_type_line.replace('MessageType: ', '')))
    state = state_type_line.replace('State: ', '')
    state_type = _control_state(message_type, state)

    return message_type, state_type, split_message

