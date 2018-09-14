# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/BadgesPage.py
import operator
import BigWorld
from debug_utils import LOG_WARNING
from dossiers2.custom.account_layout import RANKED_BADGES_BLOCK_LAYOUT
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform import settings
from gui.Scaleform.daapi.view.meta.BadgesPageMeta import BadgesPageMeta
from gui.shared.event_dispatcher import showHangar
from gui.shared.formatters import text_styles
from gui.Scaleform.locale.BADGE import BADGE
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_EMPTY_BADGE_ID = '0'

def _makeBadgeVO(badgeID, enabled, selected):
    return {'id': int(badgeID),
     'icon': settings.getBadgeIconPath(settings.BADGES_ICONS.X80, badgeID) if badgeID != _EMPTY_BADGE_ID else '',
     'title': text_styles.stats(BADGE.badgeName(badgeID)),
     'description': text_styles.main(BADGE.badgeDescriptor(badgeID)),
     'enabled': enabled,
     'selected': selected}


class BadgesPage(BadgesPageMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.instance(ILobbyContext)
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, ctx):
        super(BadgesPage, self).__init__()

    def onCloseView(self):
        showHangar()

    def _populate(self):
        super(BadgesPage, self)._populate()
        userName = BigWorld.player().name
        self.as_setStaticDataS({'header': {'closeBtnLabel': BADGE.BADGESPAGE_HEADER_CLOSEBTN_LABEL,
                    'playerText': text_styles.middleTitle(self.lobbyContext.getPlayerFullName(userName)),
                    'titleText': text_styles.promoTitle(BADGE.TITLETEXT),
                    'descText': text_styles.main(BADGE.DESCTEXT)}})
        self.__updateBadges()
        g_clientUpdateManager.addCallbacks({'stats.dossier': self.__dossierUpdateCallBack})
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged

    def onSelectBadge(self, badgeID):
        badgeID = str(badgeID)
        if badgeID == _EMPTY_BADGE_ID:
            self.rankedController.selectBadge(None)
            self.as_setSelectedBadgeImgS('')
        elif badgeID in RANKED_BADGES_BLOCK_LAYOUT:
            self.rankedController.selectBadge(badgeID)
            self.as_setSelectedBadgeImgS(settings.getBadgeIconPath(settings.BADGES_ICONS.X24, badgeID))
        else:
            LOG_WARNING('Attempt to select unknown badge {}.\nFrom {}'.format(badgeID, RANKED_BADGES_BLOCK_LAYOUT))
        return

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        super(BadgesPage, self)._dispose()

    def __dossierUpdateCallBack(self, _):
        self.__updateBadges()

    def __onServerSettingChanged(self, _):
        self.__updateBadges()

    def __updateBadges(self):
        selectedBadges = self.itemsCache.items.ranked.badges
        selectedBadge = selectedBadges[0] if selectedBadges else None
        receivedBadgesDict = self.rankedController.getReceivedBadges()
        receivedBadges = sorted(receivedBadgesDict.items(), key=operator.itemgetter(1), reverse=False)
        receivedBadgesData = [ _makeBadgeVO(badgeID, True, badgeID == selectedBadge) for badgeID, _ in receivedBadges ]
        receivedBadgesData.insert(0, _makeBadgeVO(_EMPTY_BADGE_ID, True, selectedBadge is None))
        self.as_setReceivedBadgesS({'badgesData': receivedBadgesData})
        probableBadges = self.rankedController.getAvailableBadges()
        notReceivedYet = probableBadges.difference(receivedBadgesDict)
        self.as_setNotReceivedBadgesS({'title': text_styles.highTitle(BADGE.BADGESPAGE_BODY_UNCOLLECTED_TITLE),
         'badgesData': [ _makeBadgeVO(badgeID, False, False) for badgeID in sorted(notReceivedYet) ]})
        return
