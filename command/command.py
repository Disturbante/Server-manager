from argparse import ArgumentParser, HelpFormatter, _SubParsersAction

class NoSubparsersMetavarFormatter(HelpFormatter):
    """ This is a custom formatter to remove the metavar for subparsers. 
    
        Args:
            HelpFormatter: The default formatter for argparse.
            
        Returns:
            str: The formatted action.
            
        Raises:
            AttributeError: If the action is not a subparser.
    """
    
    def _format_action(self, action):
        result = super(NoSubparsersMetavarFormatter,
                       self)._format_action(action)
        if isinstance(action, _SubParsersAction):
            return "%*s%s" % (self._current_indent, "", result.lstrip())
        return result

    def _format_action_invocation(self, action):
        if isinstance(action, _SubParsersAction):
            return ""
        return super(NoSubparsersMetavarFormatter,
                     self)._format_action_invocation(action)

    def _iter_indented_subactions(self, action):
        if isinstance(action, _SubParsersAction):
            try:
                get_subactions = action._get_subactions
            except AttributeError:
                pass
            else:
                for subaction in get_subactions():
                    yield subaction
        else:
            for subaction in super(NoSubparsersMetavarFormatter,
                                   self)._iter_indented_subactions(action):
                yield subaction
                
class CommandManager:
    """ This is a custom command manager implemented using argparse for manage CLI commands."""
    def __init__(self):
        self.parser = ArgumentParser(
            formatter_class=NoSubparsersMetavarFormatter,
            description=f'SSH Manager CLI',
            epilog='Enjoy the program! :)',
            add_help=True
        )
        self.parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
        self._add_subparsers()
        
    def _add_subparsers(self):
        subparsers = self.parser.add_subparsers(title="Commands")
        
        add = subparsers.add_parser("add", help='Add a new SSH server.')
        add.add_argument('-H', '--hostname', required=True, help='Hostname of the SSH server.')
        add.add_argument('-p', '--port', required=True, type=int, help='Port of the SSH server.')
        add.add_argument('-U', '--username', required=True, help='Username for the SSH server.')
        add.add_argument('-P', '--password', help='Password for the SSH server.')
        add.add_argument('-k', '--key', help='Key for the SSH server.')
        
        get = subparsers.add_parser("get", help='Get a SSH server.')
        get.add_argument('-i', '--id', type=int, help='ID of the SSH server.')
        
        update = subparsers.add_parser("update", help='Update a SSH server.')
        update.add_argument('-i', '--id', type=int, help='ID of the SSH server.')
        update.add_argument('-H', '--hostname', help='Hostname of the SSH server.')
        update.add_argument('-p', '--port', type=int, help='Port of the SSH server.')
        update.add_argument('-U', '--username', help='Username for the SSH server.')
        update.add_argument('-P', '--password', help='Password for the SSH server.')
        update.add_argument('-k', '--key', help='Key for the SSH server.')
        
        delete = subparsers.add_parser('delete', help='Delete a SSH server.')
        delete.add_argument('-i', '--id', type=int, help='ID of the SSH server.')
        
        lists = subparsers.add_parser("list", help='List all SSH servers.')
             
    def parse_args(self):
        return self.parser.parse_args()

