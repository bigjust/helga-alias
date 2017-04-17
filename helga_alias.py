import smokesignal

from helga import log
from helga.db import db
from helga.plugins import command

logger = log.getLogger(__name__)

def get_nick_map():

    nick_map_doc = db.alias.find_one()
    nick_map = []
    if nick_map_doc:
        nick_map = nick_map_doc['nick_map']

    return nick_map

def update_nick_map(nick_map):
    result = db.alias.replace_one({}, {'nick_map': nick_map}, True)
    logger.info('result.modified: %s', result.modified_count)

def find_aliases(nick):
    """
    Returns a list of aliases where nick is found in nick_map, else returns []
    """

    matched_nick_list = []
    for nick_list in get_nick_map():
        if nick in nick_list:
            matched_nick_list = nick_list
            break

    return matched_nick_list

@command('alias', help='Shows the nick map, should allow modification')
def alias(client, channel, nick, message, cmd, args):
    """

    Show the nick map.

    <user> !alias add <nick> <alias>
    <user> !alias remove <alias>

    Should allow 1. adds, removes, joins, splits

    """

    logger.info('args: %s', args)

    if not args:
        for nick_list in get_nick_map():
            client.msg(channel, u' '.join([unicode(alias) for alias in nick_list]))

    if args:
        if args[0] == 'add':
            if len(args) < 3:
                return 'Must specify both a nick and an alias'

            user_rename(client, args[1], args[2])

        # if args[0] == 'remove':
        #     if len(args) < 2:
        #         return 'Must specify an alias to remove'

        # potentially a nick, do a search and return aliases, if is a
        # nick in db
        if len(args) == 1:
            aliases = find_aliases(args[0])
            if aliases:
                # that's a bingo!
                return u' '.join([unicode(alias) for alias in aliases])
                #return '{}'.format(aliases)
                #return aliases


@smokesignal.on('names_reply')
def add_names(client, nicks):

    nick_map = get_nick_map()

    for nick in nicks:
        aliases = find_aliases(nick)
        if not aliases:
            nick_map.append([nick])
            update_nick_map(nick_map)

@smokesignal.on('user_rename')
def user_rename(client, oldname, newname):

    nick_map = get_nick_map()
    alias_list = find_aliases(oldname)

    if not alias_list:
        nick_map.append([oldname, newname])
    else:
        for nlist in nick_map:
            if nlist == alias_list:
                if newname not in nlist:
                    nlist.append(newname)
                break

    update_nick_map(nick_map)
