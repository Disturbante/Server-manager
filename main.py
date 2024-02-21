# from ssh import SshServerManager, SshServerType 

# ssh_manager = SshServerManager('my_database.db')

# print(ssh_manager.add_ssh_server(SshServerType('192.168.1.2', 22, 'dietpi', 'password')))

# print(ssh_manager.get_all_ssh_servers()[0].hostname)

# print(ssh_manager.update_ssh_server(1, hostname='dioniso.local'))

# print(ssh_manager.get_ssh_server(1).hostname)

# channel = ssh_manager.connect_to_ssh_server(1).connect().start_shell()

# ssh_manager.delete_ssh_server(1)

from ssh import SshServerManager
from command import CommandManager

def main(command_line=None):
    command_manager = CommandManager()
    parser = command_manager.parse_args()
    args = parser.parse_args(command_line)

    # ssh_manager = SshServerManager('my_database.db')
    # if args.subparser_name == 'add':
    #     ssh_manager.add_ssh_server(SshServerType(args.hostname, args.port, args.username, args.password, args.key))
    # elif args.subparser_name == 'get':
    #     print(ssh_manager.get_ssh_server(args.id))
    # elif args.subparser_name == 'update':
    #     ssh_manager.update_ssh_server(argsr.id, hostname=args.hostname, port=args.port, username=args.username, password=args.password, key=args.key)
    # elif args.subparser_name == 'delete':
    #     ssh_manager.delete_ssh_server(args.id)
    # elif args.subparser_name == 'list':
    #     print(ssh_manager.get_all_ssh_servers())
    # elif args.subparser_name == 'connect':
    #     ssh_manager.connect_to_ssh_server(args.id).connect().start_shell()
    # else:
    #     command_manager.parser.print_help()
    
    # manage if a user select a command add
    if args.command == 'add':
        print(args.hostname, args.port, args.username, args.password, args.key)

if __name__ == '__main__':
    main()
# import argparse


def main(command_line=None):
    parser = argparse.ArgumentParser('Blame Praise app')
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Print debug info'
    )
    subparsers = parser.add_subparsers(dest='command')
    blame = subparsers.add_parser('blame', help='blame people')
    blame.add_argument(
        '--dry-run',
        help='do not blame, just pretend',
        action='store_true'
    )
    blame.add_argument('name', nargs='+', help='name(s) to blame')
    praise = subparsers.add_parser('praise', help='praise someone')
    praise.add_argument('name', help='name of person to praise')
    praise.add_argument(
        'reason',
        help='what to praise for (optional)',
        default="no reason",
        nargs='?'
    )
    args = parser.parse_args(command_line)
    if args.debug:
        print("debug: " + str(args))
    if args.command == 'blame':
        if args.dry_run:
            print("Not for real")
        print("blaming " + ", ".join(args.name))
    elif args.command == 'praise':
        print('praising ' + args.name + ' for ' + args.reason)


# if __name__ == '__main__':
#     main()
    
