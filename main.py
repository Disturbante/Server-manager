from ssh import SshServerManager, SshServerType
from command import CommandManager

def main(command_line=None):
    command_manager = CommandManager()
    parser = command_manager.parse_args()
    args = parser.parse_args(command_line)
    
    ssh = SshServerManager("test.db")

    if args.command == 'add':
        dict_args = vars(args)
        dict_args.pop('command')
        ssh_server = SshServerType(**dict_args)
        ssh.add(ssh_server)
    elif args.command == 'get':
        print(ssh.get(args.id).password)
    elif args.command == 'update':
        dict_args = {k: v for k, v in vars(args).items() if v is not None}
        ssh.update(args.id, **dict_args)
    elif args.command == 'delete':
        ssh.delete(args.id)
    elif args.command == 'list':
        print(args.id)
        ssh.all()
    elif args.command == 'connect':
        server = ssh.connect(args.id)
        server.connect()
        server.start_shell()
        
if __name__ == '__main__':
    main()
