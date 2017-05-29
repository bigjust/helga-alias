import smokesignal

from helga import log, settings
from helga.db import db
from helga.plugins import command

OPS = getattr(settings, 'OPERATORS', [])

logger = log.getLogger(__name__)



def get_nick_map():
    """
    Returns the nick map from storage.

    returns a list of lists.

    """

    nick_map_doc = db.alias.find_one()
    nick_map = []
    if nick_map_doc:
        nick_map = nick_map_doc['nick_map']

    return nick_map

def update_nick_map(nick_map):
    """
    Stores the nick map in storage.
    """

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

    """

    if not args:
        if nick not in OPS:
            client.msg(channel, u'only operators ({}) can use this command'.format(
                ','.join(OPS)
            ))
            return

        for nick_list in get_nick_map():
            client.msg(channel, u' '.join([unicode(alias) for alias in nick_list]))

    if args:
        if args[0] == 'add':
            if len(args) < 3:
                return 'Must specify both a nick and an alias'

            user_rename(client, args[1], args[2])

        if len(args) == 1:
            aliases = find_aliases(args[0])
            if aliases:
                # that's a bingo!
                return u' '.join([unicode(alias) for alias in aliases])


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
    oldname_aliases = find_aliases(oldname)
    newname_aliases = find_aliases(newname)

    if oldname_aliases and newname_aliases:
        # nick list merge!
        nick_map.pop(nick_map.index(newname_aliases))
        nick_map[nick_map.index(oldname_aliases)].extend(newname_aliases)

    elif not oldname_aliases:
        # we haven't seen either nick, add as a new list
        nick_map.append([oldname, newname])
    else:
        # the usual, add new name to a current list
        nick_map[nick_map.index(oldname_aliases)].append(newname)

    update_nick_map(nick_map)

@smokesignal.on('user_joined')
def user_joined(client, user, channel):

    if not find_aliases(nick):
        nick_map(append([nick]))
        update_nick_map(nick_map)
