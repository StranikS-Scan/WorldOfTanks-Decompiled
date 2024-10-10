# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/prb_helpers.py
import logging
import weakref
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKeyDynamic, ViewKey
from gui.Scaleform.framework.managers.view_lifecycle_watcher import IViewLifecycleHandler
from gui.impl.gen import R
from gui.prb_control.entities.base.legacy.ctx import SetPlayerStateCtx
from gui.shared.badges import buildBadge
from gui.shared.gui_items.badge import BadgeLayouts
from gui.shared.system_factory import collectModeNameKwargsByPrbType, collectModeNameKwargsByQueueType
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _findFirstPrefixBadge(selectedBadges, itemsCache=None):
    badgeDescrs = itemsCache.items.badges.available
    if not isinstance(selectedBadges, (tuple, list)):
        if isinstance(selectedBadges, int):
            return selectedBadges
        return 0
    for sbID in selectedBadges:
        badgeDescr = badgeDescrs.get(sbID)
        if badgeDescr and badgeDescr['layout'] == BadgeLayouts.PREFIX:
            return sbID


class BadgesHelper(object):

    def __init__(self, badges=None):
        if isinstance(badges, (list, tuple)) and badges and not isinstance(badges[0], (list, tuple)):
            _logger.error('Converting badges data %s', badges)
            self.__badgesRawData = (badges, [])
        else:
            self.__badgesRawData = badges or ([], [])
        self.__badges = {}
        self.__prefixBadgeID = None
        return

    def getBadge(self):
        badgeID = self.__getBadgeID()
        if badgeID <= 0:
            return None
        else:
            if badgeID not in self.__badges:
                self.__badges[badgeID] = buildBadge(badgeID, self.__getBadgeExtraInfo())
            return self.__badges[badgeID]

    def __getBadgeID(self):
        if self.__prefixBadgeID is None:
            self.__prefixBadgeID = _findFirstPrefixBadge(self.__getSelectedBadges())
        return self.__prefixBadgeID

    def __getSelectedBadges(self):
        if not self.__badgesRawData:
            _logger.error('Invalid selected badge data')
            return []
        return self.__badgesRawData[0]

    def __getBadgeExtraInfo(self):
        if len(self.__badgesRawData) < 2:
            _logger.error('Invalid badge data %s', self.__badgesRawData)
            return None
        else:
            return self.__badgesRawData[1]


def getModeNameKwargs(entityType, isQueue=True):
    collector = collectModeNameKwargsByQueueType if isQueue else collectModeNameKwargsByPrbType
    return collector(entityType) or {}


class TrainingEntityViewLifecycleHandler(IViewLifecycleHandler):

    def __init__(self, entity):
        super(TrainingEntityViewLifecycleHandler, self).__init__([ViewKey(VIEW_ALIAS.LOBBY_HANGAR),
         ViewKey(VIEW_ALIAS.LOBBY_STORE),
         ViewKey(VIEW_ALIAS.LOBBY_STORAGE),
         ViewKey(VIEW_ALIAS.LOBBY_BARRACKS),
         ViewKey(VIEW_ALIAS.LOBBY_PROFILE),
         ViewKey(VIEW_ALIAS.VEHICLE_COMPARE),
         ViewKey(VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS),
         ViewKey(VIEW_ALIAS.LOBBY_MISSIONS),
         ViewKey(VIEW_ALIAS.LOBBY_STRONGHOLD),
         ViewKeyDynamic(R.views.lobby.techtree.VehicleTechTree()),
         ViewKeyDynamic(R.views.lobby.crew.BarracksView())])
        self.__entity = weakref.proxy(entity)

    def onViewCreated(self, _):
        self.__entity.setPlayerState(SetPlayerStateCtx(False, waitingID='prebattle/player_not_ready'))
