# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/vehicle_menu_entries/crew_auto_return_entry_sub_presenter.py
from __future__ import absolute_import
from CurrentVehicle import g_currentVehicle
from gui import SystemMessages
from gui.impl.gen.view_models.views.lobby.hangar.vehicle_menu_model import VehicleMenuModel
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.base_menu_entry_sub_presenter import BaseMenuEntrySubPresenter, EntryStateWithReason
from gui.prb_control.entities.base.listener import IPrbListener
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.gui_items.processors.tankman import TankmanAutoReturn
from gui.shared.gui_items.processors.vehicle import VehicleAutoReturnProcessor
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import decorators
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.shared import IItemsCache

class CrewAutoReturnEntrySubPresenter(BaseMenuEntrySubPresenter, IPrbListener):
    __itemsCache = dependency.descriptor(IItemsCache)
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def __init__(self, name, viewModel, parentView):
        super(CrewAutoReturnEntrySubPresenter, self).__init__(name, viewModel, parentView)
        self.__hasTankman = False

    def packEntry(self):
        self.__hasTankman = bool(self.__itemsCache.items.getInventoryTankmen(REQ_CRITERIA.TANKMAN.IS_LOCK_CREW(isLocked=False), limit=1))
        super(CrewAutoReturnEntrySubPresenter, self).packEntry()

    def onNavigate(self):
        self.__handleAutoReturnToggleSwitch()

    def _getEvents(self):
        return ((self.__platoonCtrl.onMembersUpdate, self.__onPlatoonMembersUpdate), (self._cameraController.onEnabledChange, self.__onCameraEnabledChange))

    def _getListeners(self):
        return ((events.PrebattleEvent.SWITCHED, self.__onPrbEntitySwitched, EVENT_BUS_SCOPE.LOBBY),)

    def _getState(self):
        if not self.__hasTankman:
            return VehicleMenuModel.DISABLED
        elif not g_currentVehicle.isPresent():
            return VehicleMenuModel.UNAVAILABLE
        elif g_currentVehicle.item.isCrewLocked:
            return VehicleMenuModel.UNAVAILABLE
        elif g_currentVehicle.item.lastCrew is None:
            return EntryStateWithReason(VehicleMenuModel.UNAVAILABLE, VehicleMenuModel.BATTLE_NEEDED)
        else:
            return VehicleMenuModel.ENABLED if g_currentVehicle.item.isAutoReturn else VehicleMenuModel.DISABLED

    @decorators.adisp_process('updating')
    def __handleAutoReturnToggleSwitch(self):
        if not g_currentVehicle.isPresent():
            return
        result = yield VehicleAutoReturnProcessor(g_currentVehicle.item, not g_currentVehicle.item.isAutoReturn).request()
        if result.success and g_currentVehicle.item.isAutoReturn:
            result = yield TankmanAutoReturn(g_currentVehicle.item).request()
        if not result.success:
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType, priority=NotificationPriorityLevel.MEDIUM)
        self.packEntry()

    def __onPlatoonMembersUpdate(self, *_):
        self.packEntry()

    def __onPrbEntitySwitched(self, _):
        self.packEntry()

    def __onCameraEnabledChange(self, _):
        self.packEntry()
