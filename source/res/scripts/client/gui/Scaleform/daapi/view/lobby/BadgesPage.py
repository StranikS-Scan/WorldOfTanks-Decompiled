# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/BadgesPage.py
import BigWorld
from gui import SystemMessages
from gui.Scaleform import settings
from gui.Scaleform.daapi.view.meta.BadgesPageMeta import BadgesPageMeta
from gui.shared.event_dispatcher import showHangar
from gui.shared.formatters import text_styles
from gui.Scaleform.locale.BADGE import BADGE
from gui.shared.gui_items.processors.common import BadgesSelector
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils import decorators
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

def _makeBadgeVO(badge):
    return {'id': badge.badgeID,
     'icon': badge.getBigIcon(),
     'title': text_styles.stats(badge.getUserName()),
     'description': text_styles.main(badge.getUserDescription()),
     'enabled': badge.isAchieved,
     'selected': badge.isSelected,
     'highlightIcon': badge.getHighlightIcon()}


class BadgesPage(BadgesPageMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.instance(ILobbyContext)

    def onCloseView(self):
        showHangar()

    def onSelectBadge(self, badgeID):
        self.__selectBadges((badgeID,))
        self.as_setSelectedBadgeImgS(settings.getBadgeIconPath(settings.BADGES_ICONS.X48, badgeID))

    def onDeselectBadge(self):
        self.__selectBadges()
        self.as_setSelectedBadgeImgS('')

    def _populate(self):
        super(BadgesPage, self)._populate()
        userName = BigWorld.player().name
        self.as_setStaticDataS({'header': {'closeBtnLabel': BADGE.BADGESPAGE_HEADER_CLOSEBTN_LABEL,
                    'descrTf': text_styles.main(BADGE.BADGESPAGE_HEADER_DESCR),
                    'playerText': text_styles.promoTitle(self.lobbyContext.getPlayerFullName(userName))}})
        self.__updateBadges()
        self.itemsCache.onSyncCompleted += self.__onItemsChanged

    def _dispose(self):
        self.itemsCache.onSyncCompleted -= self.__onItemsChanged
        super(BadgesPage, self)._dispose()

    def __onItemsChanged(self, updateReason, _):
        if updateReason in (CACHE_SYNC_REASON.DOSSIER_RESYNC, CACHE_SYNC_REASON.CLIENT_UPDATE):
            self.__updateBadges()

    def __updateBadges(self):
        receivedBadgesData = []
        notReceivedBadgesData = []
        for badge in sorted(self.itemsCache.items.getBadges().itervalues()):
            badgeVO = _makeBadgeVO(badge)
            if badge.isAchieved:
                receivedBadgesData.append(badgeVO)
                if badgeVO['selected']:
                    self.as_setSelectedBadgeImgS(settings.getBadgeIconPath(settings.BADGES_ICONS.X48, badgeVO['id']))
            notReceivedBadgesData.append(badgeVO)

        self.as_setReceivedBadgesS({'badgesData': receivedBadgesData})
        self.as_setNotReceivedBadgesS({'title': text_styles.highTitle(BADGE.BADGESPAGE_BODY_UNCOLLECTED_TITLE),
         'badgesData': notReceivedBadgesData})

    @decorators.process('updating')
    def __selectBadges(self, badges=None):
        result = yield BadgesSelector(badges).request()
        if result and result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
