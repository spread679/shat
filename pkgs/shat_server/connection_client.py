#!/usr/bin/env python
import pkgs.connection_core as core


class ConnectionClient(core.ConnectionCore):
    def __init__(self, connection, address):
        super().__init__(connection, address)
        self.username = ""
        self.connected = None

