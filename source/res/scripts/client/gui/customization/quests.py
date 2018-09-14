# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/quests.py
from collections import namedtuple
from gui.customization.shared import CUSTOMIZATION_TYPE, TYPE_NAME
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
_QuestData = namedtuple('QuestData', ('id', 'name', 'count'))

class Quests(object):
    _questsCache = dependency.descriptor(IEventsCache)

    def __init__(self, events, dependencies):
        self.__events = events
        self._currentVehicle = dependencies.g_currentVehicle

    def init(self):
        self._questsCache.onSyncCompleted += self._update

    def start(self):
        self._update()

    def fini(self):
        self._questsCache.onSyncCompleted -= self._update

    def _getQuestsCache(self):
        return self._questsCache

    def _update(self):
        cNationID = self._currentVehicle.item.descriptor.type.customizationNationID
        incompleteQuestItems = ({}, {}, {})
        for name, quest in self._questsCache.getEvents().items():
            for bonus in quest.getBonuses('customizations'):
                for item in bonus.getCustomizations():
                    cType = TYPE_NAME[item['custType']]
                    value = item['value']
                    if cType == CUSTOMIZATION_TYPE.EMBLEM:
                        nationId, itemId = None, item['id']
                    else:
                        nationId, itemId = item['id']
                    if nationId == cNationID or cType == CUSTOMIZATION_TYPE.EMBLEM:
                        incompleteQuestItems[cType][itemId] = _QuestData(id=quest.getID(), name=quest.getUserName(), count=value)

        self.__events.onQuestsUpdated(incompleteQuestItems)
        return
