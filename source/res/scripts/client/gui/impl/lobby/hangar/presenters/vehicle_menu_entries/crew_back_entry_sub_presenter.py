# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/vehicle_menu_entries/crew_back_entry_sub_presenter.py
from __future__ import absolute_import
import adisp
from CurrentVehicle import g_currentVehicle
from gui import SystemMessages
from gui.impl.gen.view_models.views.lobby.hangar.vehicle_menu_model import VehicleMenuModel
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries import isVehicleUnavailable
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.base_menu_entry_sub_presenter import BaseMenuEntrySubPresenter, EntryStateWithReason
from gui.prb_control.entities.base.listener import IPrbListener
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.gui_items.processors.tankman import TankmanReturn
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.shared import IItemsCache

class CrewBackEntrySubPresenter(BaseMenuEntrySubPresenter, IPrbListener):
    __itemsCache = dependency.descriptor(IItemsCache)
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def __init__(self, name, viewModel, parentView):
        super(CrewBackEntrySubPresenter, self).__init__(name, viewModel, parentView)
        self.__hasTankman = False

    def packEntry(self):
        self.__hasTankman = bool(self.__itemsCache.items.getInventoryTankmen(REQ_CRITERIA.TANKMAN.IS_LOCK_CREW(isLocked=False), limit=1))
        super(CrewBackEntrySubPresenter, self).packEntry()

    def onNavigate(self):
        self.__handleCrewBack()

    def _getEvents(self):
        return ((self.__platoonCtrl.onMembersUpdate, self.__onPlatoonMembersUpdate), (self._cameraController.onEnabledChange, self.__onCameraEnabledChange))

    def _getListeners(self):
        return ((events.PrebattleEvent.SWITCHED, self.__onPrbEntitySwitched, EVENT_BUS_SCOPE.LOBBY),)

    def _getState(self):
        if not self.__hasTankman:
            return VehicleMenuModel.DISABLED
        elif not g_currentVehicle.isPresent() or isVehicleUnavailable():
            return VehicleMenuModel.DISABLED
        vehicle = g_currentVehicle.item
        if vehicle.isCrewLocked:
            return VehicleMenuModel.DISABLED
        crew = vehicle.crew
        lastCrewIDs = vehicle.lastCrew
        if lastCrewIDs is None:
            return EntryStateWithReason(VehicleMenuModel.DISABLED, VehicleMenuModel.BATTLE_NEEDED)
        freeBerths = self.__itemsCache.items.freeTankmenBerthsCount()
        tankmenToBarracksCount = 0
        demobilizedMembersCounter = 0
        isCrewAlreadyInCurrentVehicle = True
        hasReturnableTankmen = False
        for _, tankman in crew:
            if tankman is not None:
                tankmenToBarracksCount += 1

        for lastTankmenInvID in lastCrewIDs:
            actualLastTankman = self.__itemsCache.items.getTankman(lastTankmenInvID)
            if actualLastTankman is None or actualLastTankman.isDismissed:
                demobilizedMembersCounter += 1
                isCrewAlreadyInCurrentVehicle = False
                continue
            if actualLastTankman.isInTank:
                lastTankmanVehicle = self.__itemsCache.items.getVehicle(actualLastTankman.vehicleInvID)
                if lastTankmanVehicle:
                    if lastTankmanVehicle.isLocked:
                        return VehicleMenuModel.DISABLED
                    if lastTankmanVehicle.invID != vehicle.invID:
                        isCrewAlreadyInCurrentVehicle = False
                        hasReturnableTankmen = True
                    else:
                        tankmenToBarracksCount -= 1
            hasReturnableTankmen = True
            isCrewAlreadyInCurrentVehicle = False
            freeBerths += 1

        if not hasReturnableTankmen:
            return VehicleMenuModel.DISABLED
        elif tankmenToBarracksCount > 0 and tankmenToBarracksCount > freeBerths:
            return VehicleMenuModel.DISABLED
        elif demobilizedMembersCounter > 0 and demobilizedMembersCounter == len(lastCrewIDs):
            return VehicleMenuModel.DISABLED
        elif isCrewAlreadyInCurrentVehicle:
            return VehicleMenuModel.DISABLED
        else:
            return EntryStateWithReason(VehicleMenuModel.ENABLED, VehicleMenuModel.CREW_MEMBERS_RETIRED) if 0 < demobilizedMembersCounter < len(lastCrewIDs) else VehicleMenuModel.ENABLED

    @adisp.adisp_process
    def __handleCrewBack(self):
        result = yield TankmanReturn(g_currentVehicle.item).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __onPlatoonMembersUpdate(self, *_):
        self.packEntry()

    def __onPrbEntitySwitched(self, _):
        self.packEntry()

    def __onCameraEnabledChange(self, _):
        self.packEntry()
