# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/festivity/festival/command_processor.py
import typing
import AccountCommands
from festivity.base import BaseFestivityProcessor

class FestivalCommandsProcessor(BaseFestivityProcessor):

    def buyFestivalItem(self, itemID, callback=None):
        self._perform(AccountCommands.CMD_BUY_FESTIVAL_ITEM, (itemID, 0, 0), callback)

    def setPlayerCard(self, playerCard, callback=None):
        self._perform(AccountCommands.CMD_SET_PLAYER_CARD, (playerCard,), callback)

    def markItemsAsSeen(self, itemIDs, callback=None):
        self._perform(AccountCommands.CMD_FESTIVAL_SEE_ITEMS, (itemIDs,), callback)

    def buyFestivalPackage(self, packageID, count, callback=None):
        self._perform(AccountCommands.CMD_BUY_FESTIVAL_PACKAGE, (packageID, count, 0), callback)

    def buyRandomFestivalItem(self, randomName, callback=None):
        self._perform(AccountCommands.CMD_BUY_RANDOM_FESTIVAL_ITEM, (randomName,), callback)

    def addFestivalItems(self, itemIDs, callback=None):
        self._perform(AccountCommands.CMD_ADD_FESTIVAL_ITEMS, (itemIDs,), callback)
