from ssh import SshServerManager, SshServerType 

ssh_manager = SshServerManager('my_database.db')

print(ssh_manager.add_ssh_server(SshServerType('192.168.1.2', 22, 'dietpi', 'password')))

print(ssh_manager.get_all_ssh_servers()[0].hostname)

print(ssh_manager.update_ssh_server(1, hostname='dioniso.local'))

print(ssh_manager.get_ssh_server(1).hostname)

channel = ssh_manager.connect_to_ssh_server(1).connect().start_shell()

ssh_manager.delete_ssh_server(1)
