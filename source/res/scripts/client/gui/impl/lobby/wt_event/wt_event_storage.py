# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_storage.py
import logging
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_storage_model import WtEventStorageModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_model import PortalType
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.lobby.wt_event.wt_event_base_portals_view import WtEventBasePortalsView
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showEventPortalWindow
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.wt_event.wt_event_helpers import getPortalCost
from gui.wt_event.wt_event_models_helper import setLootBoxesCount, setGuaranteedAward
from helpers import dependency
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from skeletons.gui.game_control import IEventBattlesController
_logger = logging.getLogger(__name__)

class WTEventStorageView(WtEventBasePortalsView):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.model = WtEventStorageModel()
        super(WTEventStorageView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WTEventStorageView, self).getViewModel()

    def _addListeners(self):
        super(WTEventStorageView, self)._addListeners()
        self.viewModel.onPortalClick += self.__goToPortal
        g_eventBus.addListener(events.WtEventPortalsEvent.ON_PORTAL_VIEW_CLOSED, self.__onPortalViewClose, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.WtEventPortalsEvent.ON_ALL_PORTAL_VIEWS_CLOSED, self.__goToHangar, EVENT_BUS_SCOPE.LOBBY)

    def _removeListeners(self):
        g_eventBus.removeListener(events.WtEventPortalsEvent.ON_PORTAL_VIEW_CLOSED, self.__onPortalViewClose, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.WtEventPortalsEvent.ON_ALL_PORTAL_VIEWS_CLOSED, self.__goToHangar, EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.onPortalClick -= self.__goToPortal
        super(WTEventStorageView, self)._removeListeners()

    def _updateModel(self):
        if not self._eventCtrl.isEnabled():
            return
        super(WTEventStorageView, self)._updateModel()
        with self.viewModel.transaction() as model:
            setLootBoxesCount(model.hunterPortal, EventLootBoxes.WT_HUNTER)
            model.hunterPortal.setAttemptPrice(getPortalCost(EventLootBoxes.WT_HUNTER))
            setLootBoxesCount(model.bossPortal, EventLootBoxes.WT_BOSS)
            model.bossPortal.setAttemptPrice(getPortalCost(EventLootBoxes.WT_BOSS))
            setGuaranteedAward(model.guaranteedAward)

    def __onPortalViewClose(self, _):
        self.destroyWindow()

    def __goToHangar(self, _):
        self.destroyWindow()

    def __goToPortal(self, args):
        portalType = args.get('type')
        if portalType is None:
            return
        else:
            portalType = PortalType(portalType)
            if self.__canOpenPortal(portalType):
                showEventPortalWindow(portalType=portalType, parent=self.getParentWindow())
            return

    def __canOpenPortal(self, portalType):
        return portalType in PortalType


class WtEventStorageWindow(LobbyWindow):
    __eventCtrl = dependency.descriptor(IEventBattlesController)
    __slots__ = ()

    def __init__(self, parent=None):
        super(WtEventStorageWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WTEventStorageView(R.views.lobby.wt_event.WtEventPortal()), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)

    def _onLoading(self, *args, **kwargs):
        super(WtEventStorageWindow, self)._onLoading(*args, **kwargs)
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        super(WtEventStorageWindow, self)._finalize()

    def __addListeners(self):
        self.__eventCtrl.onEventPrbChanged += self.__onEventPrbChanged

    def __removeListeners(self):
        self.__eventCtrl.onEventPrbChanged -= self.__onEventPrbChanged

    def __onEventPrbChanged(self, isActive):
        if not isActive:
            self.destroyWindow()
