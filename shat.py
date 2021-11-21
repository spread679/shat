#!/usr/bin/env python
import pkgs.shat_client.shat_client as shat_client


if __name__ == '__main__':
    try:
        socket = ('127.0.0.1', 6969)
        client = shat_client.ShatClient(socket)
        client.start_communication()
    except ConnectionRefusedError:
        print('[-] Connection refused, maybe the server is not started.')
