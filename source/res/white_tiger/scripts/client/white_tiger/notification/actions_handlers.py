# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/notification/actions_handlers.py
from helpers import dependency
from gui import SystemMessages
from gui.prb_control import prbEntityProperty
from gui.shared.utils import decorators
from gui.battle_results import RequestResultsContext
from notification.settings import NOTIFICATION_TYPE
from notification.actions_handlers import _ShowArenaResultHandler, NavigationDisabledActionHandler
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IWhiteTigerController
from white_tiger.gui.shared.event_dispatcher import showEventProgressionWindow, showEventStorageWindow
from gui.shop import showBuyLootboxOverlay

class _WTEventHandler(NavigationDisabledActionHandler):
    _gameEventCtrl = dependency.descriptor(IWhiteTigerController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    def _canNavigate(self):
        result = super(_WTEventHandler, self)._canNavigate()
        return self._gameEventCtrl.isEnabled() and result


class ShowWTBattleResultsHandler(_ShowArenaResultHandler):
    gameEventCtrl = dependency.descriptor(IWhiteTigerController)
    battleResults = dependency.descriptor(IBattleResultsService)

    def _updateNotification(self, notification):
        super(ShowWTBattleResultsHandler, self)._updateNotification(notification)
        self._showI18nMessage('#battle_results:noData', SystemMessages.SM_TYPE.Warning)

    @classmethod
    def getActions(cls):
        pass

    @prbEntityProperty
    def prbEntity(self):
        return None

    @decorators.adisp_process('loadStats')
    def _showWindow(self, notification, arenaUniqueID):
        uniqueID = long(arenaUniqueID)
        if self.prbEntity.isInQueue():
            self._showI18nMessage('#event:notifications/battleResults/disableInQueue', SystemMessages.SM_TYPE.Warning)
            return
        if not self.gameEventCtrl.isEventPrbActive():
            self._showI18nMessage('#event:notifications/battleResults/disableNotInPrebattle', SystemMessages.SM_TYPE.Warning)
            return
        result = yield self.battleResults.requestResults(RequestResultsContext(uniqueID, showImmediately=False, showIfPosted=True, resetCache=False))
        if not result:
            self._updateNotification(notification)


class OpenWTEventPortalsHandler(_WTEventHandler):

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        self._gameEventCtrl.doSelectEventPrbAndCallback(showEventStorageWindow)


class OpenWTEventCollectionHandler(_WTEventHandler):

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        self._gameEventCtrl.doSelectEventPrbAndCallback(showEventProgressionWindow)


class OpenWTEventHandler(_WTEventHandler):

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        self._gameEventCtrl.doSelectEventPrb()


class OpenWTEventQuestsHandler(_WTEventHandler):

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        self._gameEventCtrl.doSelectEventPrbAndCallback(showEventProgressionWindow)


class OpenWTEventTicketPurchasingHandler(_WTEventHandler):

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        self._gameEventCtrl.doSelectEventPrbAndCallback(showBuyLootboxOverlay)
