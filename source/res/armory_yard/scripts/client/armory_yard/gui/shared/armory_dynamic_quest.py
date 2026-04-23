# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/shared/armory_dynamic_quest.py
import constants
from armory_yard.gui.server_events.events_helpers import ArmoryDynamicQuestPostBattleInfo
from armory_yard.skeletons.armory_yard_reroll_controller import IArmoryYardRerollController
from armory_yard_constants import CONDITION_PREFIX
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.bonuses import getMergedBonusesFromDicts
from gui.server_events.event_items import PersonalQuest, IQuestBuilder
from helpers import dependency
from skeletons.gui.game_control import IArmoryYardController

class ArmoryDynamicQuest(PersonalQuest):
    __armoryYardController = dependency.descriptor(IArmoryYardController)
    __armoryYardRerollController = dependency.descriptor(IArmoryYardRerollController)
    __slots__ = ('__mainCondID', '__subCondID', '__tokenQuestID', '__rawBonuses', '__connected')

    def __init__(self, qID, data, progress=None, expiryTime=None):
        super(ArmoryDynamicQuest, self).__init__(qID, data, progress, expiryTime)
        _, mainCondID, subCondID = self.getID().split(':')
        self.__mainCondID = int(mainCondID)
        self.__subCondID = int(subCondID)
        self.__tokenQuestID = None
        self.__rawBonuses = None
        self.__connected = False
        return

    @classmethod
    def postBattleInfo(cls):
        return ArmoryDynamicQuestPostBattleInfo

    def resetConnection(self):
        self.__tokenQuestID = None
        self.__rawBonuses = None
        self.__connected = False
        return

    def getUserName(self):
        tokenQuest = self.getTokenQuest()
        return tokenQuest.getUserName() if tokenQuest is not None else super(ArmoryDynamicQuest, self).getUserName()

    def getRawBonuses(self):
        return self.__rawBonuses or self.getData().get('bonus', {})

    def getFinishTime(self):
        _, finishTime = self.__armoryYardController.getSeasonInterval()
        return finishTime or 0

    def setTokenQuestID(self, tokenQuestID):
        self.__tokenQuestID = tokenQuestID
        self.__connected = True
        tokenQuest = self.getTokenQuest()
        if tokenQuest is not None:
            self.__rawBonuses = getMergedBonusesFromDicts((self.getData().get('bonus', {}), tokenQuest.getRawBonuses()))
        return

    def getDescription(self):
        customDescription = self._data.get('description')
        if customDescription:
            return super(ArmoryDynamicQuest, self).getDescription()
        descrRes = R.strings.armory_quest_conditions.recursiveDyn(('quest_{}'.format(self.getMainID()), 'condition_{}'.format(self.getSubCondID()), 'description'))
        return backport.text(descrRes()) if descrRes else ''

    def getTokenQuestID(self):
        if not self.__connected:
            tokenQuestID = self.__armoryYardRerollController.getTokenQuestIDByConditionID(self.getMainID())
            if tokenQuestID:
                self.setTokenQuestID(tokenQuestID)
            self.__connected = True
        return self.__tokenQuestID

    def isTokenQuestCompleted(self, progress=None):
        tokenQuest = self.getTokenQuest()
        return tokenQuest.isCompleted(progress=progress) if tokenQuest is not None else None

    def getMainID(self):
        return self.__mainCondID

    def getSubCondID(self):
        return self.__subCondID

    def getTokenQuest(self):
        tokenQuestID = self.getTokenQuestID()
        return self.eventsCache.getQuestByID(tokenQuestID) if tokenQuestID is not None else None

    def getGroupID(self):
        tokenQuest = self.getTokenQuest()
        return tokenQuest.getGroupID() if tokenQuest else super(ArmoryDynamicQuest, self).getGroupID()


class ArmoryDynamicQuestBuilder(IQuestBuilder):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        return questType == constants.EVENT_TYPE.PERSONAL_QUEST and qID.startswith(CONDITION_PREFIX)

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        return ArmoryDynamicQuest(qID, data, progress)
