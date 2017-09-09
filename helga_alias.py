import smokesignal

from helga import log, settings
from helga.db import db
from helga.plugins import command

OPS = getattr(settings, 'OPERATORS', [])

logger = log.getLogger(__name__)

# Alias data structure
#
# Each record in the mongo collection will have two attributes, the
# list of aliases as detected or via commands, and optionally a
# recommended alias that would be returned for any alias in the list.
#
# {
#  'recommended_alias': 'bigjust',
#  'aliases': ['bigjust', 'justbig', 'justin'],
# }


def get_aliases():
    """
    Returns a flat list of all known aliases.
    """

    aliases = []

    for result in db.alias.find():
        aliases.extend(result['aliases'])

    return aliases


def is_alias(potential_nick):

    for result in db.alias.find():
        if potential_nick in result['aliases']:
            return True

    return False


def find_alias(nick, create_new=True):
    """
    Returns a tuple containing the key nick for an alias given, and
    the list of aliases associated with the nick.
    """

    for nick_result in db.alias.find():
        aliases = nick_result['aliases']
        if nick in aliases:
            return nick_result.get('recommended_nick', aliases[0]), nick_result['aliases']

    if create_new:
        # nick wasn't found, add new entry in alias collection
        db.alias.insert({
            'recommended_nick': nick,
            'aliases': [nick],
        })

    return nick, [nick]

@command('alias', help='Shows the nick map, should allow modification')
def alias(client, channel, nick, message, cmd, args):
    """

    <user> !alias
    Ops Only! Show the nick map.

    <user> !alias add <nick> <alias>
    Tie an alias to a nick

    <user> !alias drop <nick> <alias>
    Drops alias from the list of aliases for 'nick'

    """

    if not args:
        if nick not in OPS:
            client.msg(
                channel,
                u'only operators ({}) can use this command'.format(
                    ','.join(OPS)
                ))
            return

        for nick_result in db.alias.find():
            client.msg(channel, u'{}: {}'.format(
                nick_result['recommended_nick'],
                ', '.join(nick_result['aliases'])
            ))

    if args:
        if args[0] == 'add':
            if len(args) < 3:
                return 'Must specify both a nick and an alias'

            merge_nicks(args[1], args[2])
            client.msg(channel, 'Done!')

        if args[0] == 'drop':
            if len(args) != 2:
                return 'usage: alias drop <alias>'

            nick_key, aliases = find_alias(args[1])
            aliases.pop(aliases.index(args[1]))
            db.alias.update_one({
                'recommended_nick': nick_key,
            },{
                '$set': {'aliases': aliases},
            })

            client.msg(channel, 'Dropped.')

        if len(args) == 1:
            nick_key, aliases = find_alias(args[0])
            return u'{}: {}'.format(nick_key, ', '.join(aliases))

@smokesignal.on('names_reply')
def add_names(client, nicks):
    """
    For each nick in names reply, typically called upon entering a
    channel, call find_alias(), which would, at minimum, create a
    record for each nick found.
    """

    for nick in nicks:
        find_alias(nick)

def merge_nicks(oldname, newname):
    """
    Merge to alias lists, using the oldname as the recommended alias
    key.
    """

    oldname_key, oldname_aliases = find_alias(oldname)
    newname_key, newname_aliases = find_alias(newname)

    if oldname_key != newname_key:
        logger.debug('oldname_aliases: {}'.format(oldname_aliases))
        logger.debug('newname_aliases: {}'.format(newname_aliases))

        oldname_aliases.extend(newname_aliases)
        merged_aliases = list(set(oldname_aliases))

        logger.debug('merged_aliases: {}'.format(merged_aliases))

        db.alias.update_one({
            'recommended_nick': oldname_key,
        }, {
            '$set': {'aliases': merged_aliases},
        })

        db.alias.delete_one({
            'recommended_nick': newname_key,
        })

@smokesignal.on('user_rename')
def user_rename(client, oldname, newname):
    """
    Make sure we create an entry for each name, we'll leave merging to
    OPS.
    """

    find_alias(newname)

@smokesignal.on('user_joined')
def user_joined(client, user, channel):
    """
    Make sure we have an entry for new users that join channel.
    """

    find_alias(user)
