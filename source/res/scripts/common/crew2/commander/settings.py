# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/commander/settings.py
from crew2.commander.ranks import CommanderRanks

class CommanderSettings(object):

    def __init__(self, path):
        ranksPath = '/'.join((path, 'ranks.xml'))
        self._ranks = CommanderRanks(ranksPath)

    @property
    def ranks(self):
        return self._ranks
