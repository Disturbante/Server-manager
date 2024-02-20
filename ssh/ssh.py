from db import SshServerTable
from typing import Optional
from .ssh_info import SshServerType
import socket
import sys
# from paramiko.py3compat import u
import paramiko

# windows does not have termios...
try:
    import termios
    import tty

    has_termios = True
except ImportError:
    has_termios = False
class BaseSshServer:
    def __init__(self, server_info: SshServerType):
        self._server_info: SshServerType = server_info
        self._client: Optional[paramiko.SSHClient] = None

    @property
    def server_info(self):
        return self._server_info
    @server_info.setter
    def server_info(self, server_info: SshServerType):
        self._server_info = server_info
        
    @property
    def client(self):
        return self._client
    @client.setter
    def client(self, client: paramiko.SSHClient):
        self._client = client
    
    def alive(self) -> bool:
        return self._client is not None and self._client.get_transport().is_active()
    
    
    def start_shell(self) -> None:
        if has_termios:
            self.__posix_shell(self._client.invoke_shell())
        else:
            self.__windows_shell(self._client.invoke_shell())


    def __posix_shell(self, client: paramiko.Channel) -> None:
        import select

        oldtty = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
            client.settimeout(0.0)

            while True:
                r, w, e = select.select([client, sys.stdin], [], [])
                if client in r:
                    try:
                        x = u(client.recv(1024))
                        if len(x) == 0:
                            sys.stdout.write("\r\n*** EOF\r\n")
                            break
                        sys.stdout.write(x)
                        sys.stdout.flush()
                    except socket.timeout:
                        pass
                if sys.stdin in r:
                    x = sys.stdin.read(1)
                    if len(x) == 0:
                        break
                    client.send(x)

        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)


    def __windows_shell(self, client: paramiko.Channel) -> None:
        import threading

        sys.stdout.write(
            "Line-buffered terminal emulation. Press F6 or ^Z to send EOF.\r\n\r\n"
        )

        def writeall(sock):
            while True:
                data = sock.recv(256)
                if not data:
                    sys.stdout.write("\r\n*** EOF ***\r\n\r\n")
                    sys.stdout.flush()
                    break
                sys.stdout.write(data)
                sys.stdout.flush()

        writer = threading.Thread(target=writeall, args=(client,))
        writer.start()

        try:
            while True:
                d = sys.stdin.read(1)
                if not d:
                    break
                client.send(d)
        except EOFError:
            # user hit ^Z or F6
            pass
        
    
    def execute_command(self, command: str) -> str:
        stdin, stdout, stderr = self._client.exec_command(command)
        return stdout.read().decode('utf-8')

class PasswordSshServer(BaseSshServer):
    def __init__(self, server_info: SshServerType):
        super().__init__(server_info)
    
    def connect(self):
        if self.server_info.password is None:
            raise ValueError('Password is required to connect to server')
        try:
            self.client = paramiko.SSHClient()
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self._server_info.hostname, self.server_info.port, self.server_info.username, self.server_info.password)
        except Exception as err:
            print(f'Error connecting to server: {err}')
        
        return self
        
class KeySshServer(BaseSshServer):
    def __init__(self, server_info: SshServerType):
        super().__init__(server_info)
        
    def connect(self):
        if self.server_info.private_key_path is None:
            raise ValueError('Private key path is required to connect to server')
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.server_info.hostname, self.server_info.port, self.server_info.username, key_filename=self.server_info.private_key_path)
        return self
class SshServerManager:
    def __init__(self, db_name: str):
        self.__db = SshServerTable(db_name)
        
    def add_ssh_server(self, server: SshServerType) -> int:
        return self.__db.add_ssh_server(server)
    
    def update_ssh_server(self, server_id: int, **fields) -> None:
        self.__db.update_ssh_server(server_id, **fields)
        
    def delete_ssh_server(self, server_id: int) -> None:
        self.__db.delete_ssh_server(server_id)
        
    def get_ssh_server(self, server_id: int) -> SshServerType:
        return self.__db.get_ssh_servers(server_id)
    
    def get_all_ssh_servers(self) -> list:
        return self.__db.get_ssh_servers()
    
    def connect_to_ssh_server(self, server_id: int) -> BaseSshServer:
        server = self.__db.get_ssh_servers(server_id)
        if server.password is not None:
            return PasswordSshServer(server)
        elif server.private_key_path is not None:
            return KeySshServer(server)
        else:
            raise ValueError('No password or private key path provided for server')
        
    def close_ssh_server(self, server: BaseSshServer) -> None:
        if server.alive():
            server.close()
    