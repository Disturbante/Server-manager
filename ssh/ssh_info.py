from typing import Optional

class SshServerType:
    def __init__(self, hostname: str, port: int, username: str, password: Optional[str] = None, private_key_path: Optional[str] = None):
        self.hostname: str = hostname
        self.port: int = port
        self.username: str = username
        self.password: Optional[str] = password
        self.private_key_path: Optional[str] = private_key_path