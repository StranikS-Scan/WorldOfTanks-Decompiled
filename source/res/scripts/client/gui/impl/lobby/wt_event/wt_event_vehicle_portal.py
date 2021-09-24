# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_vehicle_portal.py
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_vehicle_portal_model import WtEventVehiclePortalModel
from gui.impl.lobby.wt_event.wt_event_sound import playVehicleAwardReceivedFromPortal
from gui.impl.lobby.wt_event.wt_event_constants import SpecialVehicleSource
from gui.impl.lobby.wt_event.wt_event_base_portal_awards_view import WtEventBasePortalAwards
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.wt_event.wt_event_helpers import getSpecialVehicle
from gui.wt_event.wt_event_models_helper import setLootBoxesCount, fillVehicleModel, fillAdditionalAwards
from gui.wt_event.wt_event_bonuses_packers import LootBoxAwardsManager
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus

class WtEventVehiclePortal(WtEventBasePortalAwards):
    __slots__ = ('__vehicleSource',)

    def __init__(self, awards=None, vehicleSource=None):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WtEventVehiclePortal(), model=WtEventVehiclePortalModel())
        super(WtEventVehiclePortal, self).__init__(settings, awards)
        self.__vehicleSource = vehicleSource

    @property
    def viewModel(self):
        return super(WtEventVehiclePortal, self).getViewModel()

    def _onLoaded(self, *args, **kwargs):
        super(WtEventVehiclePortal, self)._onLoaded(*args, **kwargs)
        playVehicleAwardReceivedFromPortal()

    def _addListeners(self):
        super(WtEventVehiclePortal, self)._addListeners()
        self.viewModel.onShowAllRewards += self.__backToRewards

    def _removeListeners(self):
        self.viewModel.onShowAllRewards -= self.__backToRewards
        super(WtEventVehiclePortal, self)._removeListeners()

    def _finalize(self):
        self.__vehicleSource = None
        super(WtEventVehiclePortal, self)._finalize()
        return

    def _updateModel(self):
        super(WtEventVehiclePortal, self)._updateModel()
        with self.viewModel.transaction() as model:
            model.setIsFromMultipleOpening(self.__vehicleSource == SpecialVehicleSource.MULTIPLE_OPENING)
            setLootBoxesCount(model.portalAvailability, self._getBoxType())
            fillVehicleModel(model.vehicle, getSpecialVehicle())
            if self._awards is not None:
                self.__setAdditionalAwards(model.additionalRewards)
        return

    def _getBoxType(self):
        return EventLootBoxes.WT_BOSS

    def _goToStorage(self):
        g_eventBus.handleEvent(events.WtEventPortalsEvent(events.WtEventPortalsEvent.ON_VEHICLE_AWARD_VIEW_CLOSED), scope=EVENT_BUS_SCOPE.LOBBY)
        self.destroyWindow()

    def __backToRewards(self):
        self.destroyWindow()

    def __setAdditionalAwards(self, model):
        groupedBonuses = LootBoxAwardsManager.getBossGroupedBonuses(self._awards)
        fillAdditionalAwards(model, groupedBonuses.additional, self._tooltipItems)


class WtEventVehiclePortalWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, awards, vehicleSource, parent=None):
        super(WtEventVehiclePortalWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WtEventVehiclePortal(awards, vehicleSource=vehicleSource), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)
