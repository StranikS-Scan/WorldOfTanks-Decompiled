# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HalloweenAccountComponent.py
from __future__ import absolute_import
import AccountCommands
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from PlayerEvents import g_playerEvents as events
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween_common.halloween_account_commands import CMD_HW_EXCHENGE_TWITCH_CON_COMMANDER, CMD_UNLOCK_TOKEN, CMD_LOCK_TOKEN, CMD_HW_ARTEFACT_OPEN, CMD_HW_BUY_BUNDLE, CMD_HW_CHOICE_STORY
from helpers import dependency

class HalloweenAccountComponent(BaseAccountExtensionComponent):
    _hwController = dependency.descriptor(IHalloweenController)

    def enqueueBattle(self, queueType, vehInvID):
        if not events.isPlayerEntityChanging:
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, (queueType, vehInvID))

    def dequeueBattle(self, queueType):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, queueType)

    def unlockToken(self, token, tokenCount=1, callback=None):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
        else:
            proxy = None
        self.account._doCmdIntStr(CMD_UNLOCK_TOKEN, tokenCount, token, proxy)
        return

    def unlockTokens(self, tokens, tokenCount=1, callback=None):
        for token in tokens:
            self.unlockToken(token, tokenCount, callback)

    def lockToken(self, token, callback=None):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
        else:
            proxy = None
        self.account._doCmdStr(CMD_LOCK_TOKEN, token, proxy)
        return

    def lockTokens(self, tokens, callback=None):
        for token in tokens:
            self.lockToken(token, callback)

    def makeStoryChoice(self, choiceID, callback=None):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(requestID, resultID, errorStr)
        else:
            proxy = None
        self.account._doCmdIntStr(CMD_HW_CHOICE_STORY, self.account.shop.getCacheRevision(), choiceID, proxy)
        return

    def openArtefact(self, artefactID, isSkipQuest, callback=None):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(requestID, resultID, errorStr)
        else:
            proxy = None
        self.account._doCmdInt2Str(CMD_HW_ARTEFACT_OPEN, self.account.shop.getCacheRevision(), int(isSkipQuest), artefactID, proxy)
        return

    def openArtefacts(self, artefactIDs, isSkipQuest, callback=None):
        for artefactID in artefactIDs:
            self.openArtefact(artefactID, isSkipQuest, callback)

    def buyBundle(self, bundleID, count=1, callback=None):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(requestID, resultID, errorStr)
        else:
            proxy = None
        self.account._doCmdInt2Str(CMD_HW_BUY_BUNDLE, self.account.shop.getCacheRevision(), int(count), bundleID, proxy)
        return

    def exchangeCommanders(self, commandersData, callback=None):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(requestID, resultID, errorStr)
        else:
            proxy = None
        intArr = [self.account.shop.getCacheRevision()]
        intArr.extend((int(count) for _, count in commandersData))
        commanderIDs = [ commanderID for commanderID, _ in commandersData ]
        self.account._doCmdIntArrStrArr(CMD_HW_EXCHENGE_TWITCH_CON_COMMANDER, intArr, commanderIDs, proxy)
        return

    def getHalloweenController(self):
        return self._hwController
