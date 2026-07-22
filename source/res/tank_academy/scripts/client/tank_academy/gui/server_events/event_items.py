# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/server_events/event_items.py
from typing import List
from constants import EVENT_TYPE
from gui.selectable_reward.constants import SELECTABLE_BONUS_NAME
from gui.server_events.event_items import ITankAcademyGroup, ITankAcademyQuest, IQuestBuilder, Quest, TokenQuest
from helpers import i18n, getLocalizedData
from tank_academy.gui.server_events.events_helpers import isTankAcademyQuestID, isTankAcademyGroupID, parseTankAcademyQuestID, parseTankAcademyGroupID, isTankAcademyOfferToken, TankAcademyQuestPostBattleInfo

class TankAcademyGroup(ITankAcademyGroup):

    def __init__(self, eID, data, order, abTestGroup):
        super(TankAcademyGroup, self).__init__(eID, data)
        self._order = order
        self._abTestGroup = abTestGroup

    def getOrder(self):
        return self._order

    def getABTestGroup(self):
        return self._abTestGroup


class TankAcademyQuestBase(ITankAcademyQuest):

    def _initTankAcademyData(self, order, abTestGroup):
        self._order = order
        self._abTestGroup = abTestGroup
        self.__vehicleOfferTokens = None
        return

    def getOrder(self):
        return self._order

    def getABTestGroup(self):
        return self._abTestGroup

    def getConditionLbl(self):
        return _getConditionLbl(self._data)

    def hasDelayedRewardBonus(self):
        return bool(self.getVehicleOfferTokens())

    def getVehicleOfferTokens(self):
        if self.__vehicleOfferTokens is None:
            self.__vehicleOfferTokens = _getQuestVehicleOfferTokens(self)
        return self.__vehicleOfferTokens


class TankAcademyTokenQuest(TokenQuest, TankAcademyQuestBase):

    def __init__(self, qID, data, progress, order, abTestGroup):
        super(TankAcademyTokenQuest, self).__init__(qID, data, progress)
        self._initTankAcademyData(order, abTestGroup)

    def _checkConditions(self):
        res = _isTankAcademyQuestAvailable(self)
        if res is None:
            res = super(TankAcademyTokenQuest, self)._checkConditions()
        return res


class TankAcademyQuest(Quest, TankAcademyQuestBase):

    def __init__(self, qID, data, progress, order, abTestGroup):
        super(TankAcademyQuest, self).__init__(qID, data, progress)
        self._initTankAcademyData(order, abTestGroup)

    def _checkConditions(self):
        res = _isTankAcademyQuestAvailable(self)
        if res is None:
            res = super(TankAcademyQuest, self)._checkConditions()
        return res

    @classmethod
    def postBattleInfo(cls):
        return TankAcademyQuestPostBattleInfo


class TankAcademyGroupQuestBuilder(IQuestBuilder):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        return False if questType != EVENT_TYPE.GROUP else isTankAcademyGroupID(qID)

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        order, abTestGroup = parseTankAcademyGroupID(qID)
        return TankAcademyGroup(qID, data, order, abTestGroup)


class TankAcademyTokenQuestBuilder(IQuestBuilder):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        return False if questType != EVENT_TYPE.TOKEN_QUEST else isTankAcademyQuestID(qID)

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        order, abTestGroup = parseTankAcademyQuestID(qID)
        return TankAcademyTokenQuest(qID, data, progress, order, abTestGroup)


class TankAcademyQuestBuilder(IQuestBuilder):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        return isTankAcademyQuestID(qID)

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        order, abTestGroup = parseTankAcademyQuestID(qID)
        return TankAcademyQuest(qID, data, progress, order, abTestGroup)


def _getConditionLbl(data):
    descriptionLbl = 'description'
    conditions = data.get('conditions')
    for itemName, itemData in conditions:
        if itemName == descriptionLbl:
            return i18n.makeString(getLocalizedData({descriptionLbl: itemData}, descriptionLbl))


def _getQuestVehicleOfferTokens(quest):
    result = []
    for bonus in quest.getBonuses():
        if bonus.getName() != SELECTABLE_BONUS_NAME:
            continue
        result.extend((token for token in bonus.getValue() if isTankAcademyOfferToken(token)))

    return result


def _isTankAcademyQuestAvailable(quest):
    if quest.isCompleted():
        return True
    else:
        if isinstance(quest, TankAcademyTokenQuest):
            if super(TankAcademyTokenQuest, quest).isCompleted():
                return True
        for item in quest.accountReqs.getConditions().items:
            if item.getName() == 'token' and item.getID() == '{}_unlock'.format(quest.getID()):
                return item.getReceivedCount() >= item.getNeededCount()

        return None
