# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/shared_utils/account_helpers/ClientHalloween.py
from pprint import pformat
import cPickle
import zlib
import AccountCommands
import Event
from halloween_shared import EVENT_STATE, extractMyDropsFromTokens
from constants import EVENT_CLIENT_DATA
from debug_utils import LOG_DEBUG_DEV
from diff_utils import synchronizeDicts

def _defaultLogger(*args):
    msg = pformat(args)
    LOG_DEBUG_DEV('\n\n[HALLOWEEN SERVER CMD RESPONSE]\n{}\n'.format(msg))


_PREFIX = '     /\\_/\\\n    ( o.o )\n     > ^ <\n***Halloween***\n'

class ClientHalloween(object):
    eventInProgress = property(lambda self: self.__state == EVENT_STATE.IN_PROGRESS)
    __em = Event.EventManager()
    onGlobalDataChanged = Event.Event(__em)
    onInventoryChanged = Event.Event(__em)

    def __init__(self, syncData):
        self.__account = None
        self.__syncData = syncData
        self.__ignore = False
        self.__tokens = {}
        self.__state = EVENT_STATE.NOT_STARTED
        self.__myDrops = {}
        return

    def getState(self):
        return self.__state

    def getMyDrops(self):
        """
        Get halloween supply drops tokens
        """
        return self.__myDrops

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def setAccount(self, account):
        self.__account = account

    def onEventsDataChanged(self):
        ingameEvents = self.__account.eventsData.get(EVENT_CLIENT_DATA.INGAME_EVENTS, None)
        if not ingameEvents:
            return
        else:
            ingameEvents = cPickle.loads(zlib.decompress(ingameEvents))
            halloweenEvent = ingameEvents['halloweenEvent']
            self.__state = halloweenEvent['state']
            self.__myDrops = extractMyDropsFromTokens(self.__tokens)
            self.onGlobalDataChanged()
            return

    def synchronize(self, isFullSync, diff):
        if self.__ignore:
            return
        else:
            self.onEventsDataChanged()
            update = diff.get('tokens', None)
            if update is not None:
                LOG_DEBUG_DEV('update tokens={}'.format(update))
                synchronizeDicts(update, self.__tokens)
                self.__myDrops = extractMyDropsFromTokens(self.__tokens)
                self.onInventoryChanged()
            return

    def __repr__(self):
        return '{} Event state ={}\ntokens = {}'.format(_PREFIX, self.__state, self.__tokens)

    def openDrop(self, dropID, callback=_defaultLogger):
        self.__account.openHalloweenSupplyDrop(dropID, callback)
