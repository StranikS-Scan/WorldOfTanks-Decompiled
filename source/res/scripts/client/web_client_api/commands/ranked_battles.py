# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/ranked_battles.py
from collections import namedtuple
from command import SchemeValidator, CommandHandler, instantiateObject
_RankedBattlesCommand = namedtuple('_RankedBattlesCommand', ('action',))
_RankedBattlesCommand.__new__.__defaults__ = (None,)
_RankedBattlesCommandScheme = {'required': (('action', basestring),)}

class RankedBattlesCommand(_RankedBattlesCommand, SchemeValidator):
    """
    Represents Ranked battles specific web command.
    """

    def __init__(self, *args, **kwargs):
        super(RankedBattlesCommand, self).__init__(_RankedBattlesCommandScheme)


def createRankedBattlesHandler(handlerFunc):
    data = {'name': 'ranked_battles',
     'cls': RankedBattlesCommand,
     'handler': handlerFunc}
    return instantiateObject(CommandHandler, data)
