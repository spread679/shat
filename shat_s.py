#!/usr/bin/env python
import pkgs.shat_server.shat_server as shat_server


if __name__ == '__main__':
    try:
        while True:
            server = shat_server.ShatServer()
            server.activate_communication()
    except KeyboardInterrupt:
        print('[+] Detected Ctrl+C. Quitting..')
