# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/seniority_awards.py
import logging
import WWISE
from gui.Scaleform.daapi.view.meta.SeniorityAwardsEntryPointMeta import SeniorityAwardsEntryPointMeta
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency, time_utils
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from gui.shared.utils.requesters.tokens_requester import TOTAL_KEY
_logger = logging.getLogger(__name__)

class SeniorityAwardsHangarEntryPoint(SeniorityAwardsEntryPointMeta):
    _itemsCache = dependency.descriptor(IItemsCache)

    def onClick(self):
        pass

    def _populate(self):
        super(SeniorityAwardsHangarEntryPoint, self)._populate()
        self.as_setDataS(getSeniorityAwardsEntryPointVO())
        self._itemsCache.onSyncCompleted += self.__onCacheResync

    def _dispose(self):
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        super(SeniorityAwardsHangarEntryPoint, self)._dispose()

    def __onCacheResync(self, _, __):
        self.as_setDataS(getSeniorityAwardsEntryPointVO())

    def playSound(self, soundID):
        WWISE.WW_eventGlobal(soundID)


def getSeniorityAwardsEntryPointVO():
    totalCount = getSeniorityAwardsBoxesCount()
    data = None
    if totalCount > 0:
        data = {'count': str(totalCount),
         'descr': backport.text(R.strings.seniority_awards.hangarEntryPoint.awardsDescr()),
         'btnLabel': backport.text(R.strings.seniority_awards.hangarEntryPoint.btn()),
         'multiplier': backport.text(R.strings.seniority_awards.hangarEntryPoint.multiplier())}
    return data


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getSeniorityAwardsAutoOpenDate(lobbyContext=None):
    config = lobbyContext.getServerSettings().getSeniorityAwardsConfig()
    autoOpenTime = config.autoOpenTimestamp()
    autoOpenLocalTime = time_utils.makeLocalServerTime(autoOpenTime)
    return backport.getLongDateFormat(autoOpenLocalTime)


def getSeniorityAwardsWidgetVisibility(lobbyContext=None):
    config = lobbyContext.getServerSettings().getSeniorityAwardsConfig()
    return config.hangarWidgetIsVisible()


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def getSeniorityAwardsBoxesCount(itemsCache=None, lobbyContext=None):
    from gui.shared.gui_items.loot_box import SENIORITY_AWARDS_LOOT_BOXES_TYPE
    config = lobbyContext.getServerSettings().getSeniorityAwardsConfig()
    totalCount = 0
    if config.isEnabled():
        itemsByType = itemsCache.items.tokens.getLootBoxesCountByType()
        seniorityAwardsCategories = itemsByType.get(SENIORITY_AWARDS_LOOT_BOXES_TYPE, {})
        totalCount = seniorityAwardsCategories.get(TOTAL_KEY, -1)
    return totalCount


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getSeniorityAwardsBox(itemsCache=None):
    from gui.shared.gui_items.loot_box import SENIORITY_AWARDS_LOOT_BOXES_TYPE
    lootBoxes = itemsCache.items.tokens.getLootBoxes()
    for item in lootBoxes.values():
        if item.getType() == SENIORITY_AWARDS_LOOT_BOXES_TYPE:
            return item

    return None
