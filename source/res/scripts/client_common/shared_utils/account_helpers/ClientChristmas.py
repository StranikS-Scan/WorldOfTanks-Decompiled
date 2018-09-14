# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/shared_utils/account_helpers/ClientChristmas.py
from pprint import pformat
import cPickle
import zlib
import AccountCommands
import Event
from christmas_shared import EVENT_STATE, extractMyToysFromTokens, extractMyChestsFromTokens
from constants import EVENT_CLIENT_DATA
from debug_utils import LOG_DEBUG_DEV
from account_helpers.diff_utils import synchronizeDicts

def _defaultLogger(*args):
    msg = pformat(args)
    LOG_DEBUG_DEV('\n\n[SERVER CMD RESPONSE]\n{}\n'.format(msg))


_PREFIX = '       \n       *\n      ***\n     *****\n    *******\n      ***\n\n ***Christmas***\n'

class ClientChristmas(object):
    eventInProgress = property(lambda self: self.__state == EVENT_STATE.IN_PROGRESS)
    __em = Event.EventManager()
    onGlobalDataChanged = Event.Event(__em)
    onInventoryChanged = Event.Event(__em)
    onTreeChanged = Event.Event(__em)

    def __init__(self, syncData):
        self.__account = None
        self.__syncData = syncData
        self.__ignore = False
        self.__knownToys = {}
        self.__tokens = {}
        self.__state = EVENT_STATE.NOT_STARTED
        self.__myToys = {}
        self.__conversions = {}
        self.__myChests = {}
        self.christmasTree = None
        self.christmasRating = 0
        return

    def getState(self):
        return self.__state

    def getMyToys(self):
        return self.__myToys

    def getAllToys(self):
        return self.__knownToys

    def getConversions(self):
        return self.__conversions

    def getMyChests(self):
        """
        Get christmas chests tokens
        """
        return self.__myChests

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
            christmasEvent = ingameEvents['christmasEvent']
            self.__knownToys = christmasEvent.get('toys', {})
            self.__myChests = extractMyChestsFromTokens(self.__tokens)
            self.__state = christmasEvent['state']
            self.__conversions = christmasEvent.get('conversions', {})
            self.__myToys = extractMyToysFromTokens(self.__tokens, self.__knownToys)
            self.onGlobalDataChanged()
            return

    def synchronize(self, isFullSync, diff):
        if self.__ignore:
            return
        else:
            self.onEventsDataChanged()
            update = diff.get('cache', {}).get('christmas', None)
            if update is not None:
                LOG_DEBUG_DEV('cache["christmas"] update={}'.format(update))
                self.christmasTree = update['christmasTree']
                self.christmasRating = update['rating']
                self.onTreeChanged()
            update = diff.get('tokens', None)
            if update is not None:
                LOG_DEBUG_DEV('update tokens={}'.format(update))
                synchronizeDicts(update, self.__tokens)
                self.__myToys = extractMyToysFromTokens(self.__tokens, self.__knownToys)
                self.__myChests = extractMyChestsFromTokens(self.__tokens)
                newToys = {}
                cleanedUpdate = {k:v or (0, 0) for k, v in update.iteritems()}
                synchronizeDicts(cleanedUpdate, newToys)
                self.onInventoryChanged(extractMyToysFromTokens(newToys, self.__knownToys))
            return

    def __repr__(self):
        return '{} state ={}\nrating ={}\nchristmasTree ={}\nmyToys ={}\nknownToys = {}'.format(_PREFIX, self.__state, self.christmasRating, self.christmasTree, self.__myToys, self.__knownToys.keys())

    def setChristmasTreeFill(self, state, callback=_defaultLogger):
        param = list(state) if state else []
        self.__account._doCmdIntArr(AccountCommands.CMD_SET_CHRISTMAS_TREE_FILL, param, callback)

    def convertToys(self, toys, callback=_defaultLogger):
        self.__account._doCmdIntArr(AccountCommands.CMD_CONVERT_TOYS, toys, callback)

    def openChest(self, callback=_defaultLogger):
        self.__account._doCmdInt3(AccountCommands.CMD_OPEN_CHEST, 0, 0, 0, callback)
