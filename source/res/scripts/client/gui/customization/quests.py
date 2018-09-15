# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/quests.py
from collections import namedtuple
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import REQUIRED_CAMOUFLAGE_TOKEN_POSTFIX
from gui.customization.shared import CUSTOMIZATION_TYPE, TYPE_NAME
from helpers import dependency
from shared_utils import first
from skeletons.gui.server_events import IEventsCache
_QuestData = namedtuple('QuestData', ('id', 'name', 'count', 'isHidden', 'requiredToken', 'isCompleted'))

def _getRequiredTokenID(quest):
    tokenReq = first(quest.accountReqs.getTokens())
    return tokenReq.getID() if tokenReq else tokenReq


class Quests(object):
    _questsCache = dependency.descriptor(IEventsCache)

    def __init__(self, events, dependencies):
        self.__events = events
        self._currentVehicle = dependencies.g_currentVehicle

    def init(self):
        self._questsCache.onSyncCompleted += self._onQuestsUpdate

    def start(self):
        self._update()

    def fini(self):
        self._questsCache.onSyncCompleted -= self._onQuestsUpdate

    def _getQuestsCache(self):
        return self._questsCache

    def _update(self):
        self.__updateQuestsWithCustomizationsBonuses()
        self.__updatePersonalMissionsCamouflagesTokens()

    def _onQuestsUpdate(self):
        self._update()
        self.__events.onQuestsItemsChanged()

    def __updateQuestsWithCustomizationsBonuses(self):
        cNationID = self._currentVehicle.item.descriptor.type.customizationNationID
        incompleteQuestItems = ({}, {}, {})
        for name, quest in self._questsCache.getAllQuests().items():
            for bonus in quest.getBonuses('customizations'):
                for item in bonus.getCustomizations():
                    cType = TYPE_NAME[item['custType']]
                    if cType == CUSTOMIZATION_TYPE.EMBLEM:
                        nationId, itemId = None, item['id']
                    else:
                        nationId, itemId = item['id']
                    if nationId == cNationID or cType == CUSTOMIZATION_TYPE.EMBLEM:
                        incompleteQuestItems[cType].setdefault(itemId, []).append(_QuestData(id=quest.getID(), name=quest.getUserName(), count=item['value'], isHidden=quest.isHidden(), requiredToken=_getRequiredTokenID(quest), isCompleted=quest.isCompleted()))

        self.__events.onQuestsUpdated(incompleteQuestItems)
        return

    def __updatePersonalMissionsCamouflagesTokens(self):
        result = {}
        for name, quest in self._questsCache.getAllQuests().iteritems():
            for bonus in quest.getBonuses('tokens'):
                for tID, token in bonus.getTokens().iteritems():
                    if tID.endswith(REQUIRED_CAMOUFLAGE_TOKEN_POSTFIX):
                        result[tID] = _QuestData(id=quest.getID(), name=quest.getUserName(), count=token.count, isHidden=quest.isHidden(), requiredToken=_getRequiredTokenID(quest), isCompleted=quest.isCompleted())

        self.__events.onPMRequiredTokensUpdated(result)
