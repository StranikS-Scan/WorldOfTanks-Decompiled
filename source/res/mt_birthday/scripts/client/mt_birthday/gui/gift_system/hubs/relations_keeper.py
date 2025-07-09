# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/gift_system/hubs/relations_keeper.py
import typing
from gui.gift_system.hubs.base.relations_keeper import GiftEventBaseKeeper
from gui.gift_system.hubs.base.relations_keeper import IGiftEventKeeper
from gui.gift_system.wrappers import ifMessagesEnabled
from gui.impl.gen import R
if typing.TYPE_CHECKING:
    from typing import List
WE_SENT_INDEX = 0

class IGiftEventBirthdayKeeper(IGiftEventKeeper):

    def getMagicPercent(self):
        raise NotImplementedError

    def getAllowMultipleSendCount(self):
        raise NotImplementedError

    def getExpireTime(self):
        raise NotImplementedError

    def updateExpireTime(self):
        raise NotImplementedError

    def getExpireDelta(self):
        raise NotImplementedError

    def isAlreadyReceivedGift(self, playerID):
        raise NotImplementedError

    def updateSentGiftState(self, playerID):
        raise NotImplementedError


class GiftEventBirthdayKeeper(GiftEventBaseKeeper, IGiftEventBirthdayKeeper):
    __slots__ = ('__magicPercent', '__allowMultipleSendCount', '__state', '__expireTime', '__expireDelta')

    def __init__(self, *args, **kwargs):
        self.__magicPercent = 0
        self.__allowMultipleSendCount = None
        self.__state = dict()
        self.__expireTime = 0
        self.__expireDelta = 0
        super(GiftEventBirthdayKeeper, self).__init__(*args, **kwargs)
        return

    def getMagicPercent(self):
        return self.__magicPercent

    def getAllowMultipleSendCount(self):
        return self.__allowMultipleSendCount

    def getExpireTime(self):
        return self.__expireTime

    def updateExpireTime(self):
        self.__expireTime += self.__expireDelta
        self.__state = dict()

    def getExpireDelta(self):
        return self.__expireDelta

    def __processState(self, state):
        for i in range(0, len(state), 3):
            spaID, weSend, weHaveBeenSent = state[i:i + 3]
            self.__state.update({spaID: [weSend, weHaveBeenSent]})

    def isAlreadyReceivedGift(self, playerID):
        return self.__state.get(playerID, [0, 0])[WE_SENT_INDEX]

    def updateSentGiftState(self, playerID):
        if playerID in self.__state:
            self.__state[playerID][WE_SENT_INDEX] += 1
        else:
            self.__state.update({playerID: [1, 0]})

    def destroy(self):
        self.__magicPercent = None
        self.__allowMultipleSendCount = None
        self.__state = None
        super(GiftEventBirthdayKeeper, self).destroy()
        return

    @ifMessagesEnabled
    def processWebState(self, webState):
        self.__magicPercent = webState.common.get('magic_percent', 0)
        self.__allowMultipleSendCount = webState.common.get('allow_multiple_send_count', 0)
        self.__processState(webState.state)
        self.__expireTime = webState.expireTime
        self.__expireDelta = webState.expireDelta
        super(GiftEventBirthdayKeeper, self).processWebState(webState)

    @staticmethod
    def getPhraseByID(phraseID):
        return R.strings.player_phrases.player.num(str(phraseID))
