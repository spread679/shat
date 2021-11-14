#!/usr/bin/env python
import enum


# @description: the different communication
class MessageType(enum.Enum):
    Configuration = 1
    Quit = 2
    Message = 3
    Connection = 4
    List = 5


# @description: prepare the header to send
# @param message_type: the message type to prepare
def get_shat_header(message_type: MessageType):
    message = 'SHAT v1.0.0\r\n'
    message += 'MessageType: ' + str(message_type.value) + '\r\n'
    return message


# @description: control the header
def control_packet(message: str):
    splitted_message = message.split('\r\n')

    message_type_line = splitted_message[1]
    type = int(message_type_line.replace('MessageType: ', ''))
    message_type = MessageType(type)
    shat_header = get_shat_header(message_type)

    if not message.startswith(shat_header):
        raise Exception('Invalid header.')

    return message_type, splitted_message

